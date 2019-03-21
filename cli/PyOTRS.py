# -*- coding: utf-8 -*-
""" cli """

import os
import stat
import click
import tempfile

from pyotrs.version import __version__
from pyotrs.lib import Client

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def load_config(config_file):
    """ load config from file and export to environment

    Args:
        config_file (str): absolute path of config file

    """

    if not os.path.isfile(config_file):
        click.secho("No config file found at: %s" % config_file, fg="yellow")
        return

    config_file_permissions = oct(stat.S_IMODE(os.stat(config_file).st_mode))
    if not (config_file_permissions == "0600" or config_file_permissions == "0o600"):
        raise Exception("Permissions to %s too open. Should be 0600!" % config_file)

    try:
        with click.open_file(config_file) as f:
            for line_raw in f:
                # ignore blank lines and lines starting with #
                # leading and trailing whitespaces are stripped
                line = line_raw.strip()
                if not line.startswith("#") and not line.startswith(" ") and not line == "":
                    key, value = line.rstrip("").split("=")
                    if not os.environ.get(key, None):  # if env key is already set preserve it
                        os.environ[key] = value

        click.secho('Using config: %s' % config_file, fg="green")

    except IOError:
        # no config file in default location; that's fine -> continue
        click.secho("No valid file found at: %s (I/O Error)" % config_file, fg="yellow")
    except ValueError as err:
        click.secho("Does not look like a valid config file: %s" % config_file, fg="yellow")
        raise Exception("Does not look like a valid config file: %s" % err)
    except Exception as err:
        click.secho("An unexpected error occurred: %s" % err, fg="red")
        raise Exception("An unexpected error occurred: %s" % err)


@click.option('-c', '--config', 'config_file', type=click.Path(dir_okay=False),
              help='Config File')
@click.version_option(version=__version__)
@click.group(context_settings=CONTEXT_SETTINGS)  # context enables -h as alias for --help
def cli(config_file=None):
    click.secho("Starting PyOTRS CLI")

    if not config_file:
        config_file = click.get_app_dir('PyOTRS', force_posix=True)
    load_config(config_file)


@click.option('--ca-cert-bundle', type=click.STRING,
              envvar='PYOTRS_CA_CERT_BUNDLE',
              help='CA CERT Bundle (Path)')
@click.option('--https-verify/--no-https-verify', default=True,
              envvar='PYOTRS_HTTPS_VERIFY',
              help='HTTPS(SSL/TLS) Certificate validation (default: enabled)')
@click.option('--articles', is_flag=True,
              help='include Articles')
@click.option('--attachments', is_flag=True,
              help='include Article Attachments')
@click.option('--store-attachments', is_flag=True,
              help='store Article Attachments to /tmp/<ticket_id>')
@click.option('--store-path', type=click.STRING,
              help='where to store Attachments (default: /tmp/pyotrs_<random_str>')
@click.option('-t', '--ticket-id', type=click.INT, prompt=True,
              envvar='PYOTRS_TICKET_ID',
              help='Ticket ID')
@click.option('-p', '--password', type=click.STRING, prompt=True, hide_input=True,
              envvar="PYOTRS_PASSWORD",
              help='Password')
@click.option('-u', '--username', type=click.STRING, prompt=True,
              envvar="PYOTRS_USERNAME",
              help='Username')
@click.option('-b', '--baseurl', type=click.STRING, prompt=True,
              envvar="PYOTRS_BASEURL",
              help='Base URL')
@cli.command(name="get")
def get(baseurl=None, username=None, password=None, ticket_id=None,
        articles=False,
        attachments=False, store_attachments=False, store_path=None,
        https_verify=True, ca_cert_bundle=None):
    """PyOTRS get command"""
    click.secho("Connecting to %s as %s.." % (baseurl, username))
    client = Client(baseurl, username, password,
                    https_verify=https_verify, ca_cert_bundle=ca_cert_bundle)
    client.session_create()

    ticket = client.ticket_get_by_id(ticket_id, articles=articles, attachments=attachments)

    if ticket:
        click.secho("Ticket: \t%s" % ticket.field_get("Title"))
        click.secho("Queue: \t\t%s" % ticket.field_get("Queue"))
        click.secho("State: \t\t%s" % ticket.field_get("State"))
        click.secho("Priority: \t%s" % ticket.field_get("Priority"))

        if store_attachments:
            if store_path:
                store_path = store_path
                if not os.path.exists(store_path):
                    os.makedirs(store_path)
            else:
                store_path = tempfile.mkdtemp(prefix="pyotrs_")

            click.secho("\nstoring attachments to: %s" % store_path)
            for article in ticket.articles:
                for attachment in article.attachments:
                    attachment.save_to_dir(folder=store_path)
                    click.secho("%s stored." % attachment)

        # click.secho("\nFull Ticket:")
        # print(ticket.to_dct())
