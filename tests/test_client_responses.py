# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # support both Python2 and 3
""" test_client_responses.py

Test for PyOTRS using **responses**
"""

# make sure (early) that parent dir (main app) is in path
import unittest2 as unittest
import responses
import requests

from pyotrs.lib import Client  # noqa


class SendRequestResponsesTests(unittest.TestCase):
    """These test check both _send_request and _build_url"""
    def test__sr_session_create(self):
        """Test _send_request session_create - mocked"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "SessionCreate"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
            rsps.add(responses.POST,
                     'http://fqdn/otrs/nph-genericinterface.pl/Webservice/'
                     'GenericTicketConnectorREST/Session',
                     json={u'SessionID': u'tMtTFDg1PxCX51dWnjue4W5oQtNsFd0k'},
                     status=200,
                     content_type='application/json')

            result = obj._send_request(payload={"UserLogin": "u-foo", "Password": "p-bar"})

        self.assertIsInstance(result, requests.Response)

    def test__sr_ticket_create(self):
        """Test _send_request ticket_create - mocked"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "TicketCreate"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
            rsps.add(responses.POST,
                     'http://fqdn/otrs/nph-genericinterface.pl/Webservice/'
                     'GenericTicketConnectorREST/Ticket',
                     json={u'ArticleID': u'2', u'TicketID': u'2', u'TicketNumber': u'000001'},
                     status=200,
                     content_type='application/json')

            result = obj._send_request(payload={"bar": "ticket-create"})

        self.assertIsInstance(result, requests.Response)

    def test__sr_ticket_get(self):
        """Test _send_request ticket_get - mocked"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "TicketGet"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
            rsps.add(responses.GET,
                     'http://fqdn/otrs/nph-genericinterface.pl/Webservice/'
                     'GenericTicketConnectorREST/Ticket/1',
                     json={u'Ticket': [{u'Age': 24040576,
                                        u'ArchiveFlag': u'n',
                                        u'ChangeBy': u'1',
                                        u'Changed': u'2016-04-13 20:41:19',
                                        u'CreateBy': u'1',
                                        u'StateType': u'open',
                                        u'TicketID': u'1',
                                        u'TicketNumber': u'2015071510123456',
                                        u'Title': u'Welcome to OTRS!',
                                        u'Type': u'Unclassified',
                                        u'TypeID': 1,
                                        u'UnlockTimeout': u'0',
                                        u'UntilTime': 0}]},
                     status=200,
                     content_type='application/json')

            result = obj._send_request(payload={"bla": "ticket-get"}, ticket_id=1)

        self.assertIsInstance(result, requests.Response)

    def test__sr_ticket_get_list(self):
        """Test _send_request ticket_get - mocked"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "TicketGetList"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
            rsps.add(responses.GET,
                     'http://fqdn/otrs/nph-genericinterface.pl/Webservice/'
                     'GenericTicketConnectorREST/TicketList',
                     json={u'Ticket': [{u'Age': 24040576,
                                        u'ArchiveFlag': u'n',
                                        u'ChangeBy': u'1',
                                        u'Changed': u'2016-04-13 20:41:19',
                                        u'CreateBy': u'1',
                                        u'StateType': u'open',
                                        u'TicketID': u'1',
                                        u'TicketNumber': u'2015071510123456',
                                        u'Title': u'Welcome to OTRS!',
                                        u'Type': u'Unclassified',
                                        u'TypeID': 1,
                                        u'UnlockTimeout': u'0',
                                        u'UntilTime': 0}]},
                     status=200,
                     content_type='application/json')

            result = obj._send_request(payload={"bla": "ticket-get"})

        self.assertIsInstance(result, requests.Response)

    def test__sr_ticket_search(self):
        """Test _send_request ticket_search - mocked"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "TicketSearch"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
            rsps.add(responses.GET,
                     'http://fqdn/otrs/nph-genericinterface.pl/Webservice/'
                     'GenericTicketConnectorREST/Ticket',
                     json={u'TicketID': [u'1']},
                     status=200,
                     content_type='application/json')

            result = obj._send_request(payload={"bla": "ticket-search"})

        self.assertIsInstance(result, requests.Response)

    def test__sr_ticket_update(self):
        """Test _send_request ticket_update - mocked"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "TicketUpdate"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
            rsps.add(responses.PATCH,
                     'http://fqdn/otrs/nph-genericinterface.pl/Webservice/'
                     'GenericTicketConnectorREST/Ticket/1',
                     json={u'TicketID': u'9', u'TicketNumber': u'000008'},
                     status=200,
                     content_type='application/json')

            result = obj._send_request(payload={"alb": "ticket-update"}, ticket_id=1)

        self.assertIsInstance(result, requests.Response)

    def test__sr_ticket_update_with_article(self):
        """Test _send_request ticket_update with article - mocked"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "TicketUpdate"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        art = {'Article': {'Subject': 'Dümmy Subject',
                           'Body': 'Hallo Bjørn,\n[kt]\n\n -- The End',
                           'TimeUnit': 0,
                           'MimeType': 'text/plain',
                           'Charset': 'UTF8'}}

        with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
            rsps.add(responses.PATCH,
                     'http://fqdn/otrs/nph-genericinterface.pl/Webservice/'
                     'GenericTicketConnectorREST/Ticket/2',
                     json={u'ArticleID': u'2', u'TicketID': u'2', u'TicketNumber': u'000002'},
                     status=200,
                     content_type='application/json')

            result = obj._send_request(payload=art, ticket_id=2)

        self.assertIsInstance(result, requests.Response)


def main():
    unittest.main()


if __name__ == '__main__':
    main()

# EOF
