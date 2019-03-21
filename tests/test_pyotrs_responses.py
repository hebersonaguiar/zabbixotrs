# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # support both Python2 and 3
""" test_pyotrs_responses.py

Test for PyOTRS using **responses**
"""

# make sure (early) that parent dir (main app) is in path
import unittest2 as unittest
import responses  # noqa
import mock  # noqa

import requests  # noqa

from pyotrs.lib import Client  # noqa
from pyotrs.lib import APIError  # noqa


class FullResponsesTests(unittest.TestCase):
    """Tests using the responses module"""
    # def test_session_create_req_mocked_valid(self):
    #     """Test session_create and _parse_and_validate_response; _send_request mocked; valid"""
    #     obj = Client(baseurl="http://fqdn",
    #                  webservicename="GenericTicketConnectorREST")
    #
    #     self.assertIsNone(obj.result_json)
    #     self.assertIsNone(obj.session_id_store.value)
    #
    #     with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
    #         rsps.add(responses.POST,
    #                  'http://fqdn/otrs/nph-genericinterface.pl/Webservice/'
    #                  'GenericTicketConnectorREST/Session',
    #                  json={u'SessionID': u'tMtTFDg1PxCX51dWnjue4W5oQtNsFd0k'},
    #                  status=200,
    #                  content_type='application/json')
    #
    #         result = obj.session_create()
    #
    #     self.assertEqual(result, True)
    #     self.assertFalse(obj._result_error)
    #     self.assertEqual(obj.operation, 'SessionCreate')
    #     self.assertEqual(obj._result_status_code, 200)
    #     self.assertDictEqual(obj.result_json,
    #                          {u'SessionID': u'tMtTFDg1PxCX51dWnjue4W5oQtNsFd0k'})
    #     self.assertEqual(obj.session_id_store.value, 'tMtTFDg1PxCX51dWnjue4W5oQtNsFd0k')
    #
    # def test_session_create_req_mocked_invalid(self):
    #     """Test session_create and _parse_and_validate_response; _send_request mocked; invalid"""
    #     obj = Client(baseurl="http://fqdn",
    #                  webservicename="GenericTicketConnectorREST")
    #
    #     self.assertIsNone(obj.result_json)
    #     self.assertIsNone(obj.session_id_store.value)
    #
    #     with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
    #         rsps.add(responses.POST,
    #                  'http://fqdn/otrs/nph-genericinterface.pl/Webservice/'
    #                  'GenericTicketConnectorREST/Session',
    #                  json={"Error": {"ErrorCode": "SessionCreate.AuthFail",
    #                                  "ErrorMessage": "SessionCreate: Authorization failing!"}},
    #                  status=200,
    #                  content_type='application/json')
    #
    #         self.assertRaisesRegex(APIError,
    #                                'Failed to access OTRS API. Check Username and Password.*',
    #                                obj.session_create)
    #
    #     self.assertTrue(obj._result_error)
    #     self.assertEqual(obj.operation, 'SessionCreate')
    #     self.assertEqual(obj._result_status_code, 200)
    #     expected_dct = {"Error": {"ErrorCode": "SessionCreate.AuthFail",
    #                               "ErrorMessage": "SessionCreate: Authorization failing!"}}
    #     self.assertDictEqual(obj.result_json, expected_dct)
    #     self.assertIsNone(obj.session_id_store.value)
    #
    # @mock.patch('pyotrs.lib.Client._parse_and_validate_response', autospec=True)
    # def test_session_create_req_mocked_failed_validation(self, mock_validate_resp):
    #     """Test session_create; _parse_and_val_response and _send_request mocked; fail vali"""
    #     obj = Client(baseurl="http://fqdn",
    #                  webservicename="GenericTicketConnectorREST")
    #
    #     self.assertIsNone(obj.result_json)
    #     self.assertIsNone(obj.session_id_store.value)
    #
    #     mock_validate_resp.return_value = False
    #
    #     with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
    #         rsps.add(responses.POST,
    #                  'http://fqdn/otrs/nph-genericinterface.pl/Webservice/'
    #                  'GenericTicketConnectorREST/Session',
    #                  json={u'SessionID': u'tMtTFDg1PxCX51dWnjue4W5oQtNsFd0k'},
    #                  status=200,
    #                  content_type='application/json')
    #
    #         result = obj.session_create()
    #
    #     self.assertFalse(result)

    # def test_ticket_update_w_art_nok_unknown_exception(self):
    #     """Test ticket_update with article - nok - exception (unknown) - mocked"""
    #     obj = Client(baseurl="http://fqdn",
    #                  webservicename="GenericTicketConnectorREST")
    #     obj.operation = "TicketUpdate"
    #     obj._result_type = obj.operation_map[obj.operation]["ResultType"]
    #
    #     art = {'Article': {'Subject': 'Dümmy Subject',
    #                        'Body': 'Hallo Bjørn,\n[kt]\n\n -- The End',
    #                        'TimeUnit': 0,
    #                        'MimeType': 'text/plain',
    #                        'Charset': 'UTF8'}}
    #
    #     with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
    #         rsps.add(responses.PATCH,
    #                  'http://fqdn/otrs/nph-genericinterface.pl/Webservice/'
    #                  'GenericTicketConnectorREST/Ticket/3',
    #                  json={u'TicketID': u'3', u'TicketNumber': u'000003'},
    #                  status=200,
    #                  content_type='application/json')
    #
    #         self.assertRaisesRegex(ValueError,
    #                                'Unknown Exception',
    #                                obj.ticket_update,
    #                                payload=art,
    #                                ticket_id=3)
    #
    # def test_ticket_update_w_article_nok_exception(self):
    #     """Test ticket_update with article - nok - reraised exception - mocked"""
    #     obj = Client(baseurl="http://fqdn",
    #                  webservicename="GenericTicketConnectorREST")
    #     obj.operation = "TicketUpdate"
    #     obj._result_type = obj.operation_map[obj.operation]["ResultType"]
    #
    #     art = {'Article': {'Subject': 'Dümmy Subject',
    #                        'Body': 'Hallo Bjørn,\n[kt]\n\n -- The End',
    #                        'TimeUnit': 0,
    #                        'MimeType': 'text/plain',
    #                        'Charset': 'UTF8'}}
    #
    #     with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
    #         rsps.add(responses.PATCH,
    #                  'http://fqdn/otrs/nph-genericinterface.pl/Webservice/'
    #                  'GenericTicketConnectorREST/Ticket/4',
    #                  json={u'ArticleID': u'', u'TicketID': u'4', u'TicketNumber': u'000004'},
    #                  status=200,
    #                  content_type='application/json')
    #
    #         self.assertRaisesRegex(ValueError,
    #                                'Unknown Ex.*',
    #                                obj.ticket_update,
    #                                payload=art,
    #                                ticket_id=4)
    #
    # def test_ticket_update_w_article_nok_exception_mocked_no_art(self):
    #     """Test ticket_update with article - nok - reraised excep mocked - no art"""
    #     obj = Client(baseurl="http://fqdn",
    #                  webservicename="GenericTicketConnectorREST")
    #     obj.operation = "TicketUpdate"
    #     obj._result_type = obj.operation_map[obj.operation]["ResultType"]
    #
    #     art = {'Article': {'Subject': 'Dümmy Subject',
    #                        'Body': 'Hallo Bjørn,\n[kt]\n\n -- The End',
    #                        'TimeUnit': 0,
    #                        'MimeType': 'text/plain',
    #                        'Charset': 'UTF8'}}
    #
    #     with responses.RequestsMock(assert_all_requests_are_fired=True) as rsps:
    #         rsps.add(responses.PATCH,
    #                  'http://fqdn/otrs/nph-genericinterface.pl/Webservice/'
    #                  'GenericTicketConnectorREST/Ticket/5',
    #                  json={u'TicketID': u'4', u'TicketNumber': u'000004'},
    #                  status=200,
    #                  content_type='application/json')
    #
    #         self.assertRaisesRegex(ValueError,
    #                                'Unknown Ex.*',
    #                                obj.ticket_update,
    #                                payload=art,
    #                                ticket_id=5)


# Main
def main():
    unittest.main()


if __name__ == '__main__':
    main()

# EOF
