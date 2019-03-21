Overview
========

|VersionBadge| |BuildStatus| |CoverageReport| |DocsBuildStatus| |LicenseBadge| |PythonVersions|


.. |VersionBadge| image:: https://badge.fury.io/py/PyOTRS.svg
    :target: https://badge.fury.io/py/PyOTRS
    :alt: |version|

.. |BuildStatus| image:: https://gitlab.com/rhab/PyOTRS/badges/master/build.svg
    :target: https://gitlab.com/rhab/PyOTRS/commits/master
    :alt: Build Status

.. |CoverageReport| image:: https://gitlab.com/rhab/PyOTRS/badges/master/coverage.svg
    :target: https://gitlab.com/rhab/PyOTRS/commits/master
    :alt: Coverage Report

.. |DocsBuildStatus| image:: https://readthedocs.org/projects/pyotrs/badge/?version=latest
    :target: https://pyotrs.readthedocs.org/en/latest/index.html
    :alt: Docs Build Status

.. |LicenseBadge| image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://gitlab.com/rhab/PyOTRS/raw/master/LICENSE
    :alt: MIT licensed

.. |PythonVersions| image:: https://img.shields.io/badge/python-2.7%2C%203.3%2C%203.4%2C%203.5%2C%203.6-blue.svg
    :alt: python: 2.7, 3.3, 3.4, 3.5, 3.6




PyOTRS is a Python wrapper for accessing `OTRS <https://www.otrs.com/>`_ (Version 5 or 6) using the
REST API.

Features
--------

Access an OTRS instance to::

    * create a new Ticket
    * get the data of a specific Ticket
    * search for Tickets
    * update existing Tickets

Some of the most notable methods provided are::

    * Client.session_create (Use credentials to "log in")
    * Client.ticket_create
    * Client.ticket_get_by_list  (takes a list)
    * Client.ticket_get_by_id  (takes an int)
    * Client.ticket_search
    * Client.ticket_update

More details can be found `here <pyotrs.html>`_

Installation
============

Dependencies
------------

*Dependencies are installed automatically*

pip::

    - python-requests
    - click (for PyOTRS Shell CLI)
    - colorama (for colors in PyOTRS Shell CLI)

Install
-------

install::

    pip install PyOTRS

**or** consider using a virtual environment::

    virtualenv venv
    source venv/bin/activate
    pip install PyOTRS

Python Usage
============

Quickstart
----------

Get Ticket with TicketID 1 from OTRS over the REST API::

    from pyotrs import Client
    client = Client("https://otrs.example.com", "root@localhost", "password")
    client.session_create()
    client.ticket_get_by_id(1)


More Examples
-------------

- instantiate a ``Client`` object called **client**
- create a session ("login") on **client**
- get the ``Ticket`` with ID 1

>>> from pyotrs import Article, Client, Ticket
>>> client = Client("http://otrs.example.com", "root@localhost", "password")
>>> client.session_create()
True

>>> my_ticket = client.ticket_get_by_id(1)
>>> my_ticket
<Ticket: 1>

>>> my_ticket.field_get("TicketNumber")
u'2010080210123456'
>>> my_ticket.field_get("Title")
u'Welcome to OTRS!'
>>> my_ticket.to_dct()  # Show complete ticket

- add an ``Article`` to ``Ticket`` with ID 1

>>> my_article = Article({"Subject": "Subj", "Body": "New Body"})
>>> client.ticket_update(1, article=my_article)
{u'ArticleID': u'3',
 u'TicketID': u'1',
 u'TicketNumber': u'2010080210123456'}


- get Articles and Attachments

>>> client.ticket_get_by_id(1, articles=1, attachments=1)
>>> my_ticket = client.result[0]

>>> my_ticket.articles
[<ArticleID: 3>, <ArticleID: 4>

>>> my_ticket.dynamic_fields
[<DynamicField: ProcessManagementActivityID: None>, <DynamicField: ProcessManagementProcessID: None>]


Get Tickets
-----------

>>> client.ticket_get_by_id(1, articles=True, attachments=True, dynamic_fields=True)
<Ticket: 1>

>>> client.ticket_get_by_list([1, 3, 4], dynamic_fields=False)
[<Ticket: 1>, <Ticket: 3>, <Ticket: 4>]


Update Tickets
--------------

>>> client.ticket_update(1, Title="New Title")
{u'TicketID': u'1', u'TicketNumber': u'2010080210123456'}

>>> my_article = Article({"Subject": "Subj", "Body": "New Body"})
>>> client.ticket_update(1, article=my_article)
{u'ArticleID': u'3',
 u'TicketID': u'1',
 u'TicketNumber': u'2010080210123456'}

>>> df = DynamicField("ExternalTicket", "1234")
>>> client.ticket_update(1, dynamic_fields=[df])
{u'TicketID': u'1', u'TicketNumber': u'2010080210123456'}


Create Tickets
--------------

OTRS requires that new Tickets have several fields filled with valid values and that an
Article is present for the new Ticket.

>>> new_ticket = Ticket.create_basic(Title="This is the Title",
                                     Queue="Raw",
                                     State=u"new",
                                     Priority=u"3 normal",
                                     CustomerUser="root@localhost")
>>> first_article = Article({"Subject": "Subj", "Body": "New Body"})
>>> client.ticket_create(new_ticket, first_article)
{u'ArticleID': u'9', u'TicketID': u'7', u'TicketNumber': u'2016110528000013'}


Article body with HTML
----------------------

PyOTRS defaults to using the MIME type "text/plain". By specifying a different type it is possible to e.g. add a HTML body.

>>> first_article = Article({"Subject": "Subj",
                             "Body": "<html><body><h1>This is a header</h1>" \
                                     "<a href='https://pyotrs.readthedocs.io/'>Link to PyOTRS Docs</a></body></html>",
                             "MimeType": "text/html"})
>>> client.ticket_update(10, first_article)
{u'ArticleID': u'29', u'TicketID': u'10', u'TicketNumber': u'2017052328000034'}


Search for Tickets
------------------

- get list of Tickets created before a date (e.g. Jan 01, 2011)

>>> from datetime import datetime
>>> client.ticket_search(TicketCreateTimeOlderDate=datetime(2011, 01, 01))
[u'1']


- get list of Tickets created less than a certain time ago (e.g. younger than 1 week)

>>> from datetime import datetime
>>> from datetime import timedelta
>>> client.ticket_search(TicketCreateTimeNewerDate=datetime.utcnow() - timedelta(days=7))
[u'66', u'65', u'64', u'63']


- show tickets with either 'open' or 'new' state in Queue 12 created over a week ago

>>> from datetime import datetime
>>> from datetime import timedelta
>>> week = datetime.utcnow() - timedelta(days=7)
>>> client.ticket_search(TicketCreateTimeOlderDate=week, States=['open', 'new'], QueueIDs=[12])

- empty result (search worked, but there are no matching tickets)

>>> client.ticket_search(Title="no such ticket")
[]

- search for content of DynamicFields

>>> df = DynamicField("ExternalTicket", search_patterns=["1234"])
>>> client.ticket_search(dynamic_fields=[df])
[u'2']

>>> df = DynamicField("ExternalTicket", search_patterns=["123*"], search_operator="Like")
>>> client.ticket_search([df])
[u'2']



Tips
----

When using **ipython** you could run into UTF8 encoding issues on Python2. This is a workaround
that can help::

    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')


**If needed** the *insecure plattform warnings* can be disabled::

    # turn off platform insecurity warnings from urllib3
    from requests.packages.urllib3 import disable_warnings
    disable_warnings()  # TODO 2016-04-23 (RH) verify this

PyOTRS Shell CLI
================

The PyOTRS Shell CLI is a kind of "proof-of-concept" for the PyOTRS wrapper library.

**Attention: PyOTRS can only retrieve Ticket data at the moment!**

Usage
-----

Get a Ticket::

    pyotrs get -b https://otrs.example.com/ -u root@localhost -p password -t 1
    Starting PyOTRS CLI
    No config file found at: /home/user/.pyotrs
    Connecting to https://otrs.example.com/ as user..
    Ticket:         Welcome to OTRS!
    Queue:          Raw
    State:          closed successful
    Priority:       3 normal

Get usage information::

    $: pyotrs -h
    Usage: PyOTRS [OPTIONS] COMMAND [ARGS]...

    Options:
      --version      Show the version and exit.
      --config PATH  Config File
      -h, --help     Show this message and exit.

    Commands:
      get  PyOTRS get command

    $:pyotrs get -h
    Starting PyOTRS CLI
    No config file found at: /home/user/.pyotrs
    Usage: PyOTRS get [OPTIONS]

      PyOTRS get command

    Options:
      -b, --baseurl TEXT              Base URL
      -u, --username TEXT             Username
      -p, --password TEXT             Password
      -t, --ticket-id INTEGER         Ticket ID
      --store-path TEXT               where to store Attachments (default:
                                      /tmp/pyotrs_<random_str>
      --store-attachments             store Article Attachments to
                                      /tmp/<ticket_id>
      --attachments                   include Article Attachments
      --articles                      include Articles
      --https-verify / --no-https-verify
                                      HTTPS(SSL/TLS) Certificate validation
                                      (default: enabled)
      --ca-cert-bundle TEXT           CA CERT Bundle (Path)
      -h, --help                      Show this message and exit.


Get a Ticket "*interactively*\"::

    $: pyotrs get
    Starting PyOTRS CLI
    No config file found at: /home/user/.pyotrs
    Baseurl: http://otrs.example.com
    Username: user
    Password:
    Ticket id: 1

    Connecting to https://otrs.example.com as user..

    Ticket:         Welcome to OTRS!
    Queue:          Raw
    State:          closed successful
    Priority:       3 normal

    Full Ticket:
    {u'Ticket': {u'TypeID': 1  [...]



Provide Config
--------------

There are four ways to provide config values::

    1. interactively when prompted
    2. as commandline arguments when calling (checkout -h/--help)
    3. as settings in the environment
    4. in a config file (default location: ~/.pyotrs)

Both the config file and the environment use the same variable names::

    PYOTRS_BASEURL=http://otrs.example.com
    PYOTRS_USERNAME=root@localhost
    PYOTRS_PASSWORD=otrs_password
    PYOTRS_HTTPS_VERIFY=True
    PYOTRS_CA_CERT_BUNDLE=


License
=======

`MIT License <http://en.wikipedia.org/wiki/MIT_License>`__
