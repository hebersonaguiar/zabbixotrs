# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # support both Python2 and 3
""" test_client.py

Test for PyOTRS Client class
"""

# make sure (early) that parent dir (main app) is in path
import unittest2 as unittest
import mock

import datetime  # noqa
import requests  # noqa

from pyotrs.lib import Article, Attachment, Client, DynamicField, Ticket  # noqa
from pyotrs.lib import ResponseParseError  # noqa
from pyotrs.lib import ArgumentMissingError, ArgumentInvalidError  # noqa
from pyotrs.lib import SessionNotCreated, SessionCreateError  # noqa
from pyotrs.lib import APIError, HTTPError  # noqa


# noinspection PyCompatibility
class ClientTests(unittest.TestCase):
    def test_init(self):
        client = Client(baseurl="http://fqdn/")
        self.assertIsInstance(client, Client)

    def test_init_no_base(self):
        self.assertRaisesRegex(ArgumentMissingError, 'baseurl', Client, '', '')

    def test_init_strip_trailing_slash1(self):
        obj = Client(baseurl="http://fqdn")
        self.assertEqual(obj.baseurl, "http://fqdn")

    def test_init_strip_trailing_slash2(self):
        obj = Client(baseurl="http://fqdn/")
        self.assertEqual(obj.baseurl, "http://fqdn")

    def test_init_session_id_store(self):
        client = Client(baseurl="http://fqdn/", session_id_file=".sid")
        self.assertEqual(client.session_id_store.file_path, '.sid')

    def test_init_session_id_store_timeout_default(self):
        client = Client(baseurl="http://fqdn/",
                        session_id_file=".sid")
        self.assertEqual(client.session_id_store.file_path, '.sid')
        self.assertEqual(client.session_id_store.timeout, 28800)

    def test_init_session_id_store_timeout(self):
        client = Client(baseurl="http://fqdn/",
                        session_id_file=".sid",
                        session_timeout=815)
        self.assertEqual(client.session_id_store.file_path, '.sid')
        self.assertEqual(client.session_id_store.timeout, 815)

    def test_init_proxies_default(self):
        client = Client(baseurl="http://fqdn/")
        self.assertDictEqual(client.proxies, {'http': '', 'https': '', 'no': ''})

    @mock.patch('pyotrs.lib.os.path.isfile', autospec=True)
    def test_init_ca_cert_bundle(self, mock_isfile):
        obj = Client(baseurl="http://fqdn/", ca_cert_bundle="/tmp/certs.pem")
        mock_isfile.return_value = True

        self.assertEqual(obj.https_verify, "/tmp/certs.pem")

    def test_init_https_verify_disabled(self):
        obj = Client(baseurl="http://fqdn/", https_verify=False)

        self.assertFalse(obj.https_verify)

    @mock.patch('pyotrs.lib.os.path.isfile', autospec=True)
    def test_init_ca_cert_bundle_non_existent(self, mock_isfile):
        mock_isfile.return_value = False
        self.assertRaisesRegex(ValueError,
                               'Certificate file does not exist.*',
                               Client,
                               baseurl="http://fqdn/",
                               ca_cert_bundle="/tmp/certs.pem")

    def test_init_proxies_override_invalid(self):
        self.assertRaisesRegex(ValueError,
                               'Proxy settings need to be provided as dict!',
                               Client,
                               baseurl="http://fqdn/",
                               proxies='http://proxy:3128')

    def test_init_proxies_override_valid(self):
        client = Client(baseurl="http://fqdn/",
                        proxies={'http': 'http://proxy:3128',
                                 'https': 'http://proxy:3128',
                                 'no': ''})
        self.assertDictEqual(client.proxies, {'http': 'http://proxy:3128',
                                              'https': 'http://proxy:3128',
                                              'no': ''})

    """
    def test_init_operation_map_override(self):
        operation_map_custom = {
            'SessionCreate': {'RequestMethod': 'POST',
                              'Route': '/Session',
                              'Result': 'SessionID'},
            'TicketCreate': {'RequestMethod': 'POST',
                             'Route': '/Ticket',
                             'Result': 'TicketID'},
            'TicketGet': {'RequestMethod': 'GET',
                          'Route': '/Ticket/:TicketID',
                          'Result': 'Ticket'},
            'TicketGetList': {'RequestMethod': 'GET',
                              'Route': '/TicketList',
                              'Result': 'Ticket'},
            'TicketSearch': {'RequestMethod': 'GET',
                             'Route': '/Ticket',
                             'Result': 'TicketID'},
            'TicketUpdate': {'RequestMethod': 'PATCH',
                             'Route': '/Ticket/:TicketID',
                             'Result': 'TicketID'}
        }
        client = Client(baseurl="http://fqdn/")
        self.assertIsInstance(client, Client)
    """

    """
    def test_init_type_map_override(self):
        type_map_custom = {
            'SessionCreate': 'SessionID',
            'TicketCreate': 'TicketID',
            'TicketGet': 'Ticket',
            'TicketGetList': 'Ticket',
            'TicketSearch': 'TicketID',
            'TicketUpdate': 'TicketID'
        }
        client = Client(baseurl="http://fqdn/",
                        webservicename="foo",
                        type_map=type_map_custom)
        self.assertIsInstance(client, Client)
    """

    def test_session_check_is_valid_no_session_id_error(self):
        """Test"""
        client = Client(baseurl="http://fqdn/")
        self.assertRaisesRegex(ArgumentMissingError,
                               'session_id',
                               client.session_check_is_valid)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_session_check_is_valid_session_id(self, mock_parse_validate, mock_send_req):
        """Test session_check_is_valid with a given valid session id"""
        obj = Client(baseurl="http://fqdn/")
        obj.session_id_store.value = "some_other_value"

        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        result = obj.session_check_is_valid(session_id="some_value")
        self.assertTrue(result)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_session_check_is_valid_invalid_session_id(self, mock_parse_validate, mock_send_req):
        """Test session_check_is_valid with a given invalid session id"""
        obj = Client(baseurl="http://fqdn/")
        obj.session_id_store.value = "some_other_value"

        mock_parse_validate.return_value = False
        mock_send_req.return_value = "mock"

        result = obj.session_check_is_valid(session_id="some_value")
        self.assertFalse(result)

    def test_init_session_default_session_timeout(self):
        client = Client(baseurl="http://fqdn/")
        self.assertEqual(client.session_timeout, 28800)

    def test_init_session_manual_session_timeout(self):
        client = Client(baseurl="http://fqdn/", session_timeout=4711)
        self.assertEqual(client.session_timeout, 4711)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_session_create_ok(self, mock_parse_validate, mock_send_req):
        """Test session create ok"""
        obj = Client(baseurl="http://fqdn/")

        obj.session_id_store.value = None
        obj.result_json = {'SessionID': 'fake'}
        obj.session_id_store.value = obj.result_json['SessionID']

        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        result = obj.session_create()
        self.assertTrue(result)
        self.assertEqual(obj.session_id_store.value, 'fake')
        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_session_create_fail(self, mock_parse_validate, mock_send_req):
        """Test session create ok"""
        obj = Client(baseurl="http://fqdn/")

        mock_parse_validate.return_value = False
        mock_send_req.return_value = "mock"

        result = obj.session_create()
        self.assertFalse(result)
        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.SessionStore.write', autospec=True)
    @mock.patch('pyotrs.Client.session_check_is_valid', autospec=True)
    @mock.patch('pyotrs.SessionStore.read', autospec=True)
    def test_session_restore_or_set_up_new_with_file_nok(self,
                                                         mock_read_s_id,
                                                         mock_is_valid,
                                                         mock_wr):
        """Tests session_restore_or_set_up_new when read from file successful but session nok"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "foobar"

        otrs_api_error = HTTPError("Failed to access OTRS. Check Hostname...")

        mock_read_s_id.return_value = "SomeSessionID1"
        mock_is_valid.side_effect = otrs_api_error

        self.assertRaisesRegex(HTTPError,
                               'Failed to access OTRS. Check Hostname...',
                               obj.session_restore_or_set_up_new)

        self.assertEqual(mock_read_s_id.call_count, 1)
        self.assertEqual(mock_is_valid.call_count, 1)
        self.assertEqual(mock_wr.call_count, 0)

    @mock.patch('pyotrs.SessionStore.write', autospec=True)
    @mock.patch('pyotrs.Client.session_check_is_valid', autospec=True)
    @mock.patch('pyotrs.SessionStore.read', autospec=True)
    def test_session_restore_or_set_up_new_with_file_ok(self,
                                                        mock_read_s_id,
                                                        mock_is_valid,
                                                        mock_wr):
        """Tests session_restore_or_set_up_new when read from file successful and session ok"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "foobar2"

        mock_read_s_id.return_value = "SomeSessionID2"
        mock_is_valid.return_value = True

        result = obj.session_restore_or_set_up_new()

        self.assertEqual(mock_read_s_id.call_count, 1)
        self.assertEqual(mock_is_valid.call_count, 1)
        self.assertEqual(mock_wr.call_count, 0)
        self.assertTrue(result)

    @mock.patch('pyotrs.SessionStore.write', autospec=True)
    @mock.patch('pyotrs.Client.session_create', autospec=True)
    @mock.patch('pyotrs.Client.session_check_is_valid', autospec=True)
    @mock.patch('pyotrs.SessionStore.read', autospec=True)
    def test_session_restore_or_set_up_new_with_file_pass(self,
                                                          mock_read_s_id,
                                                          mock_is_valid,
                                                          mock_s_create,
                                                          mock_wr):
        """Tests session_restore_or_set_up_new when file read successful but session nok"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "foobar"

        mock_read_s_id.return_value = "SomeSessionID"
        mock_is_valid.side_effect = HTTPError("Failed to access OTRS. Check Hostname...")
        mock_s_create.return_value = True

        try:
            obj.session_restore_or_set_up_new()
        except HTTPError:
            pass

        self.assertEqual(mock_read_s_id.call_count, 1)
        self.assertEqual(mock_is_valid.call_count, 1)
        self.assertEqual(mock_wr.call_count, 0)

    @mock.patch('pyotrs.SessionStore.write', autospec=True)
    @mock.patch('pyotrs.Client.session_create', autospec=True)
    @mock.patch('pyotrs.SessionStore.read', autospec=True)
    def test_session_restore_or_set_up_new_nok(self, mock_read_s_id, mock_s_create, mock_wr):
        """Tests session_restore_or_set_up_new no file; create unsuccessful"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "foobar"

        mock_read_s_id.return_value = None
        mock_s_create.return_value = False

        self.assertRaisesRegex(SessionCreateError,
                               'Failed to create a Session ID!',
                               obj.session_restore_or_set_up_new)

        self.assertEqual(mock_read_s_id.call_count, 1)
        self.assertEqual(mock_s_create.call_count, 1)
        self.assertEqual(mock_wr.call_count, 1)

    @mock.patch('pyotrs.SessionStore.write', autospec=True)
    @mock.patch('pyotrs.Client.session_create', autospec=True)
    @mock.patch('pyotrs.SessionStore.read', autospec=True)
    def test_session_restore_or_set_up_new_ok_no_wr(self, mock_read_s_id, mock_s_create, mock_wr):
        """Tests session_restore_or_set_up_new no file; create successful; write (wr) not ok"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "foobar"
        obj.result_json = {'SessionID': "the_other_sid1"}

        mock_read_s_id.return_value = None
        mock_s_create.return_value = True
        mock_wr.return_value = False

        self.assertRaisesRegex(IOError,
                               'Failed to save Session ID to file!',
                               obj.session_restore_or_set_up_new)

        self.assertEqual(mock_read_s_id.call_count, 1)
        self.assertEqual(mock_s_create.call_count, 1)
        self.assertEqual(mock_wr.call_count, 2)

    @mock.patch('pyotrs.SessionStore.write', autospec=True)
    @mock.patch('pyotrs.Client.session_create', autospec=True)
    @mock.patch('pyotrs.SessionStore.read', autospec=True)
    def test_session_restore_or_set_up_new_ok_wr_ok(self, mock_read_s_id, mock_s_create, mock_wr):
        """Tests session_restore_or_set_up_new no file; create successful; write (wr) ok"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "foobar"
        obj.result_json = {'SessionID': "the_other_sid2"}

        mock_read_s_id.return_value = None
        mock_s_create.return_value = True
        mock_wr.return_value = True

        obj.session_restore_or_set_up_new()

        self.assertEqual(mock_read_s_id.call_count, 1)
        self.assertEqual(mock_s_create.call_count, 1)
        self.assertEqual(mock_wr.call_count, 2)

    def test_ticket_create_no_session_created(self):
        """Test ticket_create - no ticket specified"""
        obj = Client(baseurl="http://fqdn")
        self.assertRaisesRegex(SessionNotCreated,
                               'Call session_create.*',
                               obj.ticket_create)

    def test_ticket_create_no_ticket(self):
        """Test ticket_create - no ticket specified"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        self.assertRaisesRegex(ArgumentMissingError,
                               'Ticket',
                               obj.ticket_create)

    def test_ticket_create_no_article(self):
        """Test ticket_create - no article specified"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        tic = Ticket(dct={'Title': 'foo'})

        self.assertRaisesRegex(ArgumentMissingError,
                               'Article',
                               obj.ticket_create, ticket=tic)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_create_mocked_none(self, mock_parse_validate, mock_send_req):
        """Test ticket_create - mocked result None"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        tic = Ticket(dct={'Title': 'foo'})
        art = Article({'Subject': 'mySubject',
                       'Body': 'myBody',
                       'TimeUnit': 0,
                       'MimeType': 'text/plain',
                       'Charset': 'UTF8'})

        mock_parse_validate.return_value = False
        mock_send_req.return_value = "mock"

        result = obj.ticket_create(ticket=tic, article=art)
        self.assertFalse(result)
        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_create_mocked_true(self, mock_parse_validate, mock_send_req):
        """Test ticket_create - mocked result """
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        tic = Ticket(dct={'Title': 'foo'})
        art = Article({'Subject': 'mySubject',
                       'Body': 'myBody',
                       'TimeUnit': 0,
                       'MimeType': 'text/plain',
                       'Charset': 'UTF8'})

        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.ticket_create(ticket=tic, article=art)
        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_create_mocked_attachment_true(self, mock_parse_validate, mock_send_req):
        """Test ticket_create - mocked attachment result """
        obj = Client(baseurl="http://fqdn")
        att1 = Attachment.create_basic("mFyCg==", "text/plain", "foo.txt")
        att2 = Attachment.create_basic("YmFyCg==", "text/plain", "dümmy.txt")
        obj.session_id_store.value = "some_session_id"
        tic = Ticket(dct={'Title': 'foo'})
        art = Article({'Subject': 'mySubject',
                       'Body': 'myBody',
                       'TimeUnit': 0,
                       'MimeType': 'text/plain',
                       'Charset': 'UTF8'})

        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.ticket_create(ticket=tic, article=art, attachments=[att1, att2])
        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_create_mocked_dynamic_field_true(self, mock_parse_validate, mock_send_req):
        """Test ticket_create - mocked dynamic field result """
        obj = Client(baseurl="http://fqdn")
        dyn1 = DynamicField(name="firstname", value="Jane")
        dyn2 = DynamicField.from_dct({'Name': 'lastname', 'Value': 'Doe'})
        obj.session_id_store.value = "some_session_id"
        tic = Ticket(dct={'Title': 'foo'})
        art = Article({'Subject': 'mySubject',
                       'Body': 'myBody',
                       'TimeUnit': 0,
                       'MimeType': 'text/plain',
                       'Charset': 'UTF8'})

        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.ticket_create(ticket=tic, article=art, dynamic_fields=[dyn1, dyn2])
        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    def test_ticket_get_no_session_created(self):
        """Test ticket_create - no ticket specified"""
        obj = Client(baseurl="http://fqdn")
        self.assertRaisesRegex(SessionNotCreated,
                               'Call session_create.*',
                               obj.ticket_get_by_id, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_get_by_id_fail(self, mock_parse_validate, mock_send_req):
        """Tests ticket_get_by_id fail"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"

        mock_parse_validate.return_value = False
        mock_send_req.return_value = "mock"

        result = obj.ticket_get_by_id(1)

        self.assertFalse(result)
        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_get_by_id_ok(self, mock_parse_validate, mock_send_req):
        """Tests ticket_get_by_id ok"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"

        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"
        obj.result = [Ticket._dummy()]

        result = obj.ticket_get_by_id(1)

        self.assertIsInstance(result, Ticket)
        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    def test_ticket_get_list_no_session_created(self):
        """Test ticket_create - no ticket specified"""
        obj = Client(baseurl="http://fqdn")
        self.assertRaisesRegex(SessionNotCreated,
                               'Call session_create.*',
                               obj.ticket_get_by_list, [1])

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_get_by_list_fail(self, mock_parse_validate, mock_send_req):
        """Tests ticket_get_by_list fail"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"

        mock_parse_validate.return_value = False
        mock_send_req.return_value = "mock"

        result = obj.ticket_get_by_list([1])

        self.assertFalse(result)
        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    def test_ticket_get_by_list_fail_int_provided(self):
        """Tests ticket_get_by_list fail int was provided"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"

        self.assertRaisesRegex(ArgumentInvalidError,
                               "Please provide list of IDs!",
                               obj.ticket_get_by_list,
                               1)

    def test_ticket_get_by_list_fail_string_provided(self):
        """Tests ticket_get_by_list fail int was provided"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"

        self.assertRaisesRegex(ArgumentInvalidError,
                               "Please provide list of IDs!",
                               obj.ticket_get_by_list,
                               "4711")

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_get_by_list_ok(self, mock_parse_validate, mock_send_req):
        """Tests ticket_get_by_list ok"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"

        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"
        obj.result = [Ticket._dummy()]

        result = obj.ticket_get_by_list([1])

        self.assertIsInstance(result[0], Ticket)
        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_get_by_list_ok_two(self, mock_parse_validate, mock_send_req):
        """Tests ticket_get_by_list ok"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"

        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"
        obj.result = [Ticket._dummy(), Ticket._dummy()]

        result = obj.ticket_get_by_list([1, 2])

        self.assertIsInstance(result[0], Ticket)
        self.assertEqual(len(result), 2)
        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    def test_ticket_get_by_number_with_int(self):
        """Tests ticket_get_by_number provided int not str -> fail"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"

        self.assertRaisesRegex(ArgumentInvalidError,
                               'Provide ticket_number as str/unicode. Got ticket_number as int.',
                               obj.ticket_get_by_number, ticket_number=1)

    @mock.patch('pyotrs.Client.ticket_search', autospec=True)
    def test_ticket_get_by_number_with_string_no_result(self, mock_ticket_search):
        """Tests ticket_get_by_number provided as int -> ok"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"

        mock_ticket_search.return_value = False
        result = obj.ticket_get_by_number("SomeOtherNumber")
        self.assertFalse(result)
        self.assertEqual(mock_ticket_search.call_count, 1)

    @mock.patch('pyotrs.Client.ticket_get_by_id', autospec=True)
    @mock.patch('pyotrs.Client.ticket_search', autospec=True)
    def test_ticket_get_by_number_one_result_fail(self, mock_ticket_search, mock_t_get_id):
        """Tests ticket_get_by_number - one result but fail to get"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"

        mock_ticket_search.return_value = [u'11']
        mock_t_get_id.return_value = False

        result = obj.ticket_get_by_number("4711")

        self.assertFalse(result)
        self.assertEqual(mock_ticket_search.call_count, 1)
        self.assertEqual(mock_t_get_id.call_count, 1)

    @mock.patch('pyotrs.Client.ticket_get_by_id', autospec=True)
    @mock.patch('pyotrs.Client.ticket_search', autospec=True)
    def test_ticket_get_by_number_one_result_ok(self, mock_ticket_search, mock_t_get_id):
        """Tests ticket_get_by_number - one result - get ok"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"

        mock_ticket_search.return_value = [u'12']
        mock_t_get_id.return_value = Ticket._dummy()
        obj.result = [Ticket._dummy()]

        result = obj.ticket_get_by_number("4712")

        self.assertIsInstance(result, Ticket)
        self.assertEqual(mock_ticket_search.call_count, 1)
        self.assertEqual(mock_t_get_id.call_count, 1)

    @mock.patch('pyotrs.Client.ticket_search', autospec=True)
    def test_ticket_get_by_number_with_string_three_results(self, mock_ticket_search):
        """Tests ticket_get_by_number provided as int; 3 results -> nok"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"

        mock_ticket_search.return_value = [1, 2, 3]
        self.assertRaisesRegex(ValueError,
                               'Found more than one result for Ticket Number: SomeONumber',
                               obj.ticket_get_by_number,
                               'SomeONumber')

        self.assertEqual(mock_ticket_search.call_count, 1)

    def test_ticket_search_no_session_created(self):
        """Test ticket_create - no ticket specified"""
        obj = Client(baseurl="http://fqdn")
        self.assertRaisesRegex(SessionNotCreated,
                               'Call session_create.*',
                               obj.ticket_search)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_search_ticket_id(self, mock_parse_validate, mock_send_req):
        """Tests ticket_search ticket id"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        obj.result = [1]
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.ticket_search(TicketID="1")

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_search_ticket_id_fail(self, mock_parse_validate, mock_send_req):
        """Tests ticket_search ticket id"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        obj.result = [1]
        mock_parse_validate.return_value = False
        mock_send_req.return_value = "mock"

        obj.ticket_search(TicketID="1")

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_search_datetime(self, mock_parse_validate, mock_send_req):
        """Tests ticket_search datetime"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        obj.result = [1]

        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.ticket_search(TicketCreateTimeOlderDate=datetime.datetime.utcnow())

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_search_dynamic_field(self, mock_parse_validate, mock_send_req):
        """Tests ticket_search datetime"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        obj.result = [1]

        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        dyn1 = DynamicField("SomeFieldName", search_patterns=["foo", "bar"])

        obj.ticket_search(dynamic_fields=[dyn1])

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_search_dynamic_field_single_(self, mock_parse_validate, mock_send_req):
        """Tests ticket_search datetime"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        obj.result = [1]

        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        dyn1 = DynamicField("SomeFieldName", search_patterns=["foo", "bar"])

        obj.ticket_search(dynamic_fields=dyn1)

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_search_dynamic_field_two(self, mock_parse_validate, mock_send_req):
        """Tests ticket_search datetime"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        obj.result = [1]

        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        dyn1 = DynamicField("SomeFieldName", search_patterns="foo")

        obj.ticket_search(Title="FooBar", dynamic_fields=[dyn1])

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client.ticket_search')
    def test_ticket_search_full_text(self, mock_ticket_search):
        """Tests ticket_search full text"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        obj.result = [1]

        mock_ticket_search.return_value = True

        obj.ticket_search_full_text("Something")

        expected = [({'Body': u'%Something%',
                      'ContentSearch': u'OR',
                      'FullTextIndex': u'1',
                      'Subject': u'%Something%'},)]

        self.assertEqual(mock_ticket_search.call_count, 1)
        self.assertEqual(mock_ticket_search.call_args_list, expected)
        mock_ticket_search.assert_called_once_with(Body=u'%Something%',
                                                   ContentSearch=u'OR',
                                                   FullTextIndex=u'1',
                                                   Subject=u'%Something%')

    def test_ticket_update_no_session_created(self):
        """Test ticket_create - no ticket specified"""
        obj = Client(baseurl="http://fqdn")
        self.assertRaisesRegex(SessionNotCreated,
                               'Call session_create.*',
                               obj.ticket_update, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_update_queue_id_ok(self, mock_parse_validate, mock_send_req):
        """Tests ticket_update queue_id ok"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.ticket_update(1, QueueID="1")

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_update_queue_id_nok(self, mock_parse_validate, mock_send_req):
        """Tests ticket_update queue_id nok"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = False
        mock_send_req.return_value = "mock"

        result = obj.ticket_update(1, QueueID="1")

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)
        self.assertFalse(result)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_update_article_nok(self, mock_parse_validate, mock_send_req):
        """Tests ticket_update article nok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        art = Article({'Subject': 'mySubject',
                       'Body': 'myBody',
                       'TimeUnit': 0,
                       'MimeType': 'text/plain',
                       'Charset': 'UTF8'})

        mock_parse_validate.return_value = False
        mock_send_req.return_value = "mock"

        result = obj.ticket_update(1, article=art)

        self.assertFalse(result)
        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_update_attach_list_no_article_nok(self, mock_parse_validate, mock_send_req):
        """Tests ticket_update attachment list no article nok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = False
        mock_send_req.return_value = "mock"

        att1 = Attachment.create_basic("mFyCg==", "text/plain", "foo.txt")
        att2 = Attachment.create_basic("YmFyCg==", "text/plain", "dümmy.txt")

        self.assertRaisesRegex(ArgumentMissingError,
                               'To create an attachment an article is needed!',
                               obj.ticket_update,
                               1, attachments=[att1, att2])

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_update_attachment_list_article_nok(self, mock_parse_validate, mock_send_req):
        """Tests ticket_update attachment list article nok"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"

        payload = {u'Attachment': [{u'Content': u'mFyCg==',
                                    u'ContentType': u'text/plain',
                                    u'Filename': u'foo.txt'},
                                   {u'Content': u'YmFyCg==',
                                    u'ContentType': u'text/plain',
                                    u'Filename': u'dümmy.txt'}],
                   u'TicketID': 8,
                   u'SessionID': "some_session_id",
                   u'Article': {u'Body': u'myBodyAtt',
                                u'Subject': u'mySubjectAtt',
                                u'TimeUnit': 4,
                                u'MimeType': u'text/plain',
                                u'Charset': u'UTF8'}}

        art = Article({'Subject': 'mySubjectAtt',
                       'Body': 'myBodyAtt',
                       'TimeUnit': 4,
                       'MimeType': 'text/plain',
                       'Charset': 'UTF8'})

        att1 = Attachment.create_basic("mFyCg==", "text/plain", "foo.txt")
        att2 = Attachment.create_basic("YmFyCg==", "text/plain", "dümmy.txt")

        mock_parse_validate.return_value = False
        mock_send_req.return_value = "mock"

        result = obj.ticket_update(8, article=art, attachments=[att1, att2])

        self.assertFalse(result)
        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)
        mock_send_req.assert_called_once_with(payload, 8)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_update_dynamic_field_list_nok(self, mock_parse_validate, mock_send_req):
        """Tests ticket_update dynamic field list nok"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"

        payload = {u'DynamicField': [{u'Name': u'firstname', u'Value': u'Jane'},
                                     {u'Name': u'lastname', u'Value': u'Doe'}],
                   u'TicketID': 7,
                   u'SessionID': "some_session_id",
                   u'Article': {u'Body': u'myBody',
                                u'Subject': u'mySubject',
                                u'TimeUnit': 0,
                                u'MimeType': u'text/plain',
                                u'Charset': u'UTF8'}}

        art = Article({'Subject': 'mySubject',
                       'Body': 'myBody',
                       'TimeUnit': 0,
                       'MimeType': 'text/plain',
                       'Charset': 'UTF8'})

        dyn1 = DynamicField(name="firstname", value="Jane")
        dyn2 = DynamicField.from_dct({'Name': 'lastname', 'Value': 'Doe'})

        mock_parse_validate.return_value = False
        mock_send_req.return_value = "mock"

        result = obj.ticket_update(7, article=art, dynamic_fields=[dyn1, dyn2])

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)
        self.assertFalse(result)
        mock_send_req.assert_called_once_with(payload, 7)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_update_set_pending_ok(self, mock_parse_validate, mock_send_req):
        """Tests ticket_update_set_pending ok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.ticket_update_set_pending(1)

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_ticket_update_set_pending_nok(self, mock_parse_validate, mock_send_req):
        """Tests ticket_update_set_pending nok"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = False
        mock_send_req.return_value = "mock"

        result = obj.ticket_update_set_pending(1)

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)
        self.assertFalse(result)

    def test_faq_language_list_no_session_created(self):
        """Test faq_language_list - no session"""
        obj = Client(baseurl="http://fqdn")
        self.assertRaisesRegex(SessionNotCreated,
                               'Call session_create.*',
                               obj.faq_language_list)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_faq_language_list(self, mock_parse_validate, mock_send_req):
        """Tests faq_language_list - ok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.faq_language_list()

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    def test_faq_category_list_no_session_created(self):
        """Test faq_category_list - no session"""
        obj = Client(baseurl="http://fqdn")
        self.assertRaisesRegex(SessionNotCreated,
                               'Call session_create.*',
                               obj.faq_category_list)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_faq_category_list(self, mock_parse_validate, mock_send_req):
        """Tests faq_category_list - ok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.faq_category_list()

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    def test_faq_public_faq_get_no_session_created(self):
        """Test faq_public_faq_get - no session"""
        obj = Client(baseurl="http://fqdn")
        self.assertRaisesRegex(SessionNotCreated,
                               'Call session_create.*',
                               obj.faq_public_faq_get)

    def test_faq_public_faq_get_no_item_id(self):
        """Test faq_public_faq_get - no item id"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"

        self.assertRaisesRegex(ArgumentMissingError,
                               'item_ids is required',
                               obj.faq_public_faq_get)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_faq_public_faq_get(self, mock_parse_validate, mock_send_req):
        """Tests faq_public_faq_get - with str, no attachment content - ok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.faq_public_faq_get("1", attachment_contents=False)

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_faq_public_faq_get_list(self, mock_parse_validate, mock_send_req):
        """Tests faq_public_faq_get - with list - ok """
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.faq_public_faq_get([1, 2])

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    def test_faq_public_faq_search_no_session_created(self):
        """Test faq_public_faq_search - no session"""
        obj = Client(baseurl="http://fqdn")
        self.assertRaisesRegex(SessionNotCreated,
                               'Call session_create.*',
                               obj.faq_public_faq_search)

    def test_faq_public_faq_search_invalid_search_dict(self):
        """Test faq_public_faq_search - invalid search dict"""
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        self.assertRaisesRegex(ArgumentInvalidError,
                               'Expecting dict for search_dict!',
                               obj.faq_public_faq_search, search_dict="this is no dict")

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_faq_public_faq_search(self, mock_parse_validate, mock_send_req):
        """Tests faq_public_faq_search - ok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.faq_public_faq_search("foobar")

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_faq_public_faq_search_number(self, mock_parse_validate, mock_send_req):
        """Tests faq_public_faq_search - number - ok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"
        obj.result = []

        obj.faq_public_faq_search(number="21")

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_faq_public_faq_search_title(self, mock_parse_validate, mock_send_req):
        """Tests faq_public_faq_search - title - ok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"
        obj.result = [u'1']

        obj.faq_public_faq_search(title="Test-Title")

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_faq_public_faq_search_search_dict(self, mock_parse_validate, mock_send_req):
        """Tests faq_public_faq_search - search_dict - ok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"
        obj.result = [u'3', u'4']

        obj.faq_public_faq_search(search_dict={"Keyword": "Password"})

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    def test_link_add_no_session_created(self):
        """Test link_add - no session"""
        obj = Client(baseurl="http://fqdn")
        self.assertRaisesRegex(SessionNotCreated,
                               'Call session_create.*',
                               obj.link_add, 1, 2)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_link_add(self, mock_parse_validate, mock_send_req):
        """Tests link_add - ok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.link_add(1, 2)

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    def test_link_delete_no_session_created(self):
        """Test link_delete - no session"""
        obj = Client(baseurl="http://fqdn")
        self.assertRaisesRegex(SessionNotCreated,
                               'Call session_create.*',
                               obj.link_delete, 1, 2)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_link_delete(self, mock_parse_validate, mock_send_req):
        """Tests link_delete - ok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.link_delete(1, 2)

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    def test_link_delete_all_no_session_created(self):
        """Test link_delete_all - no session"""
        obj = Client(baseurl="http://fqdn")
        self.assertRaisesRegex(SessionNotCreated,
                               'Call session_create.*',
                               obj.link_delete_all, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_link_delete_all(self, mock_parse_validate, mock_send_req):
        """Tests link_delete_all - ok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.link_delete_all(1)

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    def test_link_list_no_session_created(self):
        """Test link_list - no session"""
        obj = Client(baseurl="http://fqdn")
        self.assertRaisesRegex(SessionNotCreated,
                               'Call session_create.*',
                               obj.link_list, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_link_list(self, mock_parse_validate, mock_send_req):
        """Tests link_list - ok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.link_list(1)

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_link_list_dst(self, mock_parse_validate, mock_send_req):
        """Tests link_list - with dst ok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.link_list(1, dst_object_type="Ticket")

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_link_list_dst_type_dir(self, mock_parse_validate, mock_send_req):
        """Tests link_list - with all ok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.link_list(1, dst_object_type="Ticket", link_type="ParentChild", direction="Source")

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    def test_link_possible_link_list_no_session_created(self):
        """Test link_possible_link_list - no session"""
        obj = Client(baseurl="http://fqdn")
        self.assertRaisesRegex(SessionNotCreated,
                               'Call session_create.*',
                               obj.link_possible_link_list)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_link_possible_link_list(self, mock_parse_validate, mock_send_req):
        """Tests link_possible_link_list - ok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.link_possible_link_list()

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_link_possible_link_list_fail(self, mock_parse_validate, mock_send_req):
        """Tests link_possible_link_list - fail"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = False
        mock_send_req.return_value = "mock"

        obj.link_possible_link_list()

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    def test_link_possible_objects_list_no_session_created(self):
        """Test link_possible_objects_list - no session"""
        obj = Client(baseurl="http://fqdn")
        self.assertRaisesRegex(SessionNotCreated,
                               'Call session_create.*',
                               obj.link_possible_objects_list)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_link_possible_objects_list(self, mock_parse_validate, mock_send_req):
        """Tests link_possible_objects_list - ok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.link_possible_objects_list()

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_link_possible_objects_list_fail(self, mock_parse_validate, mock_send_req):
        """Tests link_possible_objects_list - fail"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = False
        mock_send_req.return_value = "mock"

        obj.link_possible_objects_list()

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    def test_link_possible_types_list_no_session_created(self):
        """Test link_possible_types_list - no session"""
        obj = Client(baseurl="http://fqdn")
        self.assertRaisesRegex(SessionNotCreated,
                               'Call session_create.*',
                               obj.link_possible_types_list)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_link_possible_types_list(self, mock_parse_validate, mock_send_req):
        """Tests link_possible_types_list - ok"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = True
        mock_send_req.return_value = "mock"

        obj.link_possible_types_list()

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    @mock.patch('pyotrs.Client._send_request')
    @mock.patch('pyotrs.Client._parse_and_validate_response', autospec=True)
    def test_link_possible_types_list_fail(self, mock_parse_validate, mock_send_req):
        """Tests link_possible_types_list - fail"""
        # create object
        obj = Client(baseurl="http://fqdn")
        obj.session_id_store.value = "some_session_id"
        mock_parse_validate.return_value = False
        mock_send_req.return_value = "mock"

        obj.link_possible_types_list()

        self.assertEqual(mock_parse_validate.call_count, 1)
        self.assertEqual(mock_send_req.call_count, 1)

    def test__build_url_with_different_webservice_path(self):
        """Test _build_url with a different webservice path"""
        obj = Client(baseurl="http://fqdn", webservice_path="/nph-genericinterface.pl/Webservice/")
        obj.operation = "SessionCreate"

        self.assertEqual("http://fqdn/nph-genericinterface.pl/Webservice/"
                         "GenericTicketConnectorREST/Session",
                         obj._build_url())

    def test__build_url_session_create(self):
        """Test _build_url for session create"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "SessionCreate"

        self.assertEqual("http://fqdn/otrs/nph-genericinterface.pl/Webservice/"
                         "GenericTicketConnectorREST/Session",
                         obj._build_url())

    def test__build_url_ticket_create(self):
        """Test _build_url for ticket create"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "TicketCreate"

        self.assertEqual("http://fqdn/otrs/nph-genericinterface.pl/Webservice/"
                         "GenericTicketConnectorREST/Ticket",
                         obj._build_url())

    def test__build_url_ticket_get(self):
        """Test _build_url for ticket get"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "TicketGet"

        self.assertEqual("http://fqdn/otrs/nph-genericinterface.pl/Webservice/"
                         "GenericTicketConnectorREST/Ticket/508",
                         obj._build_url(508))

    def test__build_url_ticket_get_list(self):
        """Test _build_url for ticket get list"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "TicketGetList"

        self.assertEqual("http://fqdn/otrs/nph-genericinterface.pl/Webservice/"
                         "GenericTicketConnectorREST/TicketList",
                         obj._build_url())

    def test__build_url_ticket_search(self):
        """Test _build_url for ticket search"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "TicketSearch"

        self.assertEqual("http://fqdn/otrs/nph-genericinterface.pl/Webservice/"
                         "GenericTicketConnectorREST/Ticket",
                         obj._build_url())

    def test__build_url_ticket_update(self):
        """Test _build_url for ticket update"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "TicketUpdate"

        self.assertEqual("http://fqdn/otrs/nph-genericinterface.pl/Webservice/"
                         "GenericTicketConnectorREST/Ticket/509",
                         obj._build_url(509))

    def test__build_url_ticket_update_invalid(self):
        """Test _build_url for ticket update when required TicketID is not given"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "TicketUpdate"

        self.assertRaisesRegex(ValueError,
                               "TicketID is None but Route requires TicketID.*",
                               obj._build_url)

    def test__build_url_faq_language_list(self):
        """Test _build_url for faq_language_list"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "PublicCategoryList"

        self.assertEqual("http://fqdn/otrs/nph-genericinterface.pl/Webservice/"
                         "GenericFAQConnectorREST/PublicCategoryList",
                         obj._build_url())

    def test__build_url_faq_category_list(self):
        """Test _build_url for faq_category_list"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "LanguageList"

        self.assertEqual("http://fqdn/otrs/nph-genericinterface.pl/Webservice/"
                         "GenericFAQConnectorREST/LanguageList",
                         obj._build_url())

    def test__build_url_link_add(self):
        """Test _build_url for link_add"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "LinkAdd"

        self.assertEqual("http://fqdn/otrs/nph-genericinterface.pl/Webservice/"
                         "GenericLinkConnectorREST/LinkAdd",
                         obj._build_url())

    def test__build_url_link_possible_link_list(self):
        """Test _build_url for link_possible_list_list"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "PossibleLinkList"

        self.assertEqual("http://fqdn/otrs/nph-genericinterface.pl/Webservice/"
                         "GenericLinkConnectorREST/PossibleLinkList",
                         obj._build_url())

    def test__send_request_no_payload(self):
        """Test _send_request no payload"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "TicketSearch"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        self.assertRaisesRegex(ArgumentMissingError,
                               'payload',
                               obj._send_request)

    def test__send_request_invalid_method(self):
        # ""Test _send_request with invalid http method ""
        operation_mapping_invalid = {
            'Name': 'GenericTicketConnectorREST',
            'Config': {
                'SessionCreate':
                    {'Result': 'SessionID', 'RequestMethod': 'FB', 'Route': '/Session'},
                'TicketCreate':
                    {'Result': 'TicketID', 'RequestMethod': 'FB', 'Route': '/Ticket'},
                'TicketGet':
                    {'Result': 'Ticket', 'RequestMethod': 'FB', 'Route': '/Ticket/:TicketID'},
                'TicketGetList':
                    {'Result': 'Ticket', 'RequestMethod': 'FB', 'Route': '/TicketList'},
                'TicketSearch':
                    {'Result': 'TicketID', 'RequestMethod': 'FB', 'Route': '/Ticket'},
                'TicketUpdate':
                    {'Result': 'TicketID', 'RequestMethod': 'FB', 'Route': '/Ticket/:TicketID'}
            }
        }

        obj = Client(baseurl="http://fqdn", webservice_config_ticket=operation_mapping_invalid)

        obj.operation = "TicketSearch"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        self.assertRaisesRegex(ValueError,
                               'invalid http_method',
                               obj._send_request,
                               payload={"foo": "bar"})

    @mock.patch('pyotrs.lib.requests.request')
    def test__send_request_ok(self, mock_requests_req):
        """Tests _send_request ok"""
        obj = Client(baseurl="http://fqdn", user_agent="MyCustomClient v0.1")
        obj.operation = "TicketSearch"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        mock_requests_req.return_value.result = True
        mock_requests_req.return_value.status_code = 200
        mock_requests_req.return_value.content = "all good"

        mocked_result = obj._send_request(payload={'foo': 'bar'})

        self.assertEqual(mock_requests_req.call_count, 1)
        self.assertTrue(mocked_result.result)

    @mock.patch('pyotrs.lib.requests.request', autospec=True)
    def test__send_request_http_status_code_nok(self, mock_requests_req):
        """Tests _send_request fail http status code not 200"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "TicketSearch"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        mock_requests_req.return_value.result = False
        mock_requests_req.return_value.status_code = 500
        mock_requests_req.return_value.content = "no me gusta"

        self.assertRaisesRegex(HTTPError,
                               'Received HTTP Error. Check Hostname and We.*',
                               obj._send_request,
                               payload={'fooEs': 'barSp'})

        self.assertEqual(mock_requests_req.call_count, 1)

    @mock.patch('pyotrs.lib.requests.request', autospec=True)
    def test__send_request_fail(self, mock_requests_req):
        """Tests _send_request fail"""
        obj = Client(baseurl="http://fqdn")
        obj.operation = "TicketSearch"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        mock_requests_req.side_effect = Exception("Some Exception")

        self.assertRaisesRegex(HTTPError,
                               'Failed to access OTRS. Check Hostname, Proxy, SSL.*',
                               obj._send_request,
                               payload={'foo': 'bar'})

        self.assertEqual(mock_requests_req.call_count, 1)

    def test__validate_response_init_invalid(self):
        """Test _validate_response_init_invalid - missing response """
        obj = Client(baseurl="http://localhost")

        self.assertRaisesRegex(ValueError,
                               'requests.Response object expected!',
                               obj._parse_and_validate_response,
                               'just_some_string')

    def test__validate_response_invalid_operation(self):
        """Test _validate_response with an invalid operation"""
        obj = Client(baseurl="http://localhost")
        obj.operation = "DoTheMagicRainDance"
        # obj._result_type = obj.ws_config[obj.operation]["Result"]

        mocked_response = mock.Mock(spec=requests.Response)
        mocked_response.status_code = 200
        mocked_response.json.return_value = {}

        self.assertRaisesRegex(ValueError,
                               'invalid operation',
                               obj._parse_and_validate_response,
                               mocked_response)

    def test__validate_response_operation_session_create(self):
        """Test _validate_response with SessionCreate"""
        obj = Client(baseurl="http://localhost")
        obj.operation = "SessionCreate"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        mocked_response = mock.Mock(spec=requests.Response)
        mocked_response.status_code = 200
        mocked_response.json.return_value = {u'SessionID': u'tMtTFDg1PxCXfoobarue4W5oQtNsFd0k'}

        obj._parse_and_validate_response(mocked_response)

        self.assertEqual(obj._result_type, 'SessionID')

    def test__validate_response_operation_ticket_get(self):
        """Test _validate_response with TicketGet"""
        obj = Client(baseurl="http://localhost")
        obj.operation = "TicketGetList"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        tkt = {u'Ticket': [{u'Age': 24040576,
                            u'CreateBy': u'1',
                            u'CustomerID': None,
                            u'CustomerUserID': None,
                            u'DynamicField': [{u'Name': u'ProcessManagementActivityID',
                                               u'Value': None},
                                              {u'Name': u'ProcessManagementProcessID',
                                               u'Value': None}],
                            u'EscalationResponseTime': u'0'}]}

        mocked_response = mock.Mock(spec=requests.Response)
        mocked_response.status_code = 200
        mocked_response.json.return_value = tkt

        obj._parse_and_validate_response(mocked_response)

        self.assertEqual(obj._result_type, 'Ticket')
        self.assertDictEqual(obj.result_json, tkt)

    def test__validate_response_operation_ticket_create(self):
        """Test _validate_response with TicketCreate"""
        obj = Client(baseurl="http://localhost")
        obj.operation = "TicketCreate"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        mocked_response = mock.Mock(spec=requests.Response)
        mocked_response.status_code = 200
        mocked_response.json.return_value = {u'ArticleID': u'26',
                                             u'TicketID': u'9',
                                             u'TicketNumber': u'000008'}

        obj._parse_and_validate_response(mocked_response)

        self.assertEqual(obj._result_type, 'TicketID')
        self.assertDictEqual(obj.result_json, {u'ArticleID': u'26',
                                               u'TicketID': u'9',
                                               u'TicketNumber': u'000008'})

    def test__validate_response_operation_ticket_update(self):
        """Test _validate_response with TicketUpdate"""
        obj = Client(baseurl="http://localhost")
        obj.operation = "TicketCreate"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        mocked_response = mock.Mock(spec=requests.Response)
        mocked_response.status_code = 200
        mocked_response.json.return_value = {u'TicketID': u'9', u'TicketNumber': u'000008'}

        obj._parse_and_validate_response(mocked_response)
        self.assertEqual(obj._result_type, 'TicketID')
        self.assertDictEqual(obj.result_json, {u'TicketID': u'9',
                                               u'TicketNumber': u'000008'})

    def test__validate_response_operation_ticket_search(self):
        """Test _validate_response with TicketSearch"""
        obj = Client(baseurl="http://localhost")
        obj.operation = "TicketSearch"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        mocked_response = mock.Mock(spec=requests.Response)
        mocked_response.status_code = 200
        mocked_response.json.return_value = {u'TicketID': [u'9']}

        obj._parse_and_validate_response(mocked_response)
        self.assertEqual(obj._result_type, 'TicketID')
        self.assertDictEqual(obj.result_json, {u'TicketID': [u'9']})

    def test__validate_response_operation_ticket_search_empty(self):
        """Test _validate_response with TicketSearch with empty result"""
        obj = Client(baseurl="http://localhost")
        obj.operation = "TicketSearch"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        mocked_response = mock.Mock(spec=requests.Response)
        mocked_response.status_code = 200
        mocked_response.json.return_value = {}

        obj._parse_and_validate_response(mocked_response)
        self.assertEqual(obj._result_type, 'TicketID')
        self.assertDictEqual(obj.result_json, {})

    def test__validate_response_operation_ticket_search_nonsense(self):
        """Test _validate_response with TicketSearch with a nonsence response"""
        obj = Client(baseurl="http://localhost")
        obj.operation = "TicketSearch"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        mocked_response = mock.Mock(spec=requests.Response)
        mocked_response.status_code = 200
        mocked_response.json.return_value = {u'FooBar': [u'1', u'3']}

        self.assertRaises(ResponseParseError,
                          obj._parse_and_validate_response,
                          mocked_response)
        self.assertEqual(obj._result_type, 'TicketID')
        self.assertTrue(obj._result_error)
        self.assertDictEqual(obj.result_json, {u'FooBar': [u'1', u'3']})

    def test__validate_response_operation_faq_public_faq_search_ok(self):
        """Test _validate_response with faq_public_faq_search ok"""
        obj = Client(baseurl="http://localhost")
        obj.operation = "PublicFAQSearch"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        mocked_response = mock.Mock(spec=requests.Response)
        mocked_response.status_code = 200
        mocked_response.json.return_value = {"ID": [u"3", u"2", u"1"]}

        obj._parse_and_validate_response(mocked_response)
        self.assertEqual(obj._result_type, 'ID')
        self.assertDictEqual(obj.result_json, {"ID": [u"3", u"2", u"1"]})

    def test__validate_response_operation_faq_public_faq_search_no_result(self):
        """Test _validate_response with faq_public_faq_search no result"""
        obj = Client(baseurl="http://localhost")
        obj.operation = "PublicFAQSearch"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        mocked_response = mock.Mock(spec=requests.Response)
        mocked_response.status_code = 200
        _dct = {u'Error': {u'ErrorCode': u'PublicFAQSearch.NotFAQData',
                           u'ErrorMessage': u'PublicFAQSearch: Could not get FAQ data in '
                                            u'Kernel::GenericInterface::Operation::FAQ::'
                                            u'PublicFAQSearch::Run()'}}
        mocked_response.json.return_value = _dct

        obj._parse_and_validate_response(mocked_response)
        self.assertEqual(obj._result_type, 'ID')

        self.assertDictEqual(obj.result_json, _dct)

    def test__validate_response_operation_link_add_ok(self):
        """Test _validate_response with link_add ok"""
        obj = Client(baseurl="http://localhost")
        obj.operation = "LinkAdd"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        mocked_response = mock.Mock(spec=requests.Response)
        mocked_response.status_code = 200
        mocked_response.json.return_value = {"Success": 1}

        obj._parse_and_validate_response(mocked_response)
        self.assertEqual(obj._result_type, 'LinkAdd')
        self.assertDictEqual(obj.result_json, {"Success": 1})

    def test__validate_response_operation_link_list_ok(self):
        """Test _validate_response with link_list ok"""
        obj = Client(baseurl="http://localhost")
        obj.operation = "LinkList"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        mocked_response = mock.Mock(spec=requests.Response)
        mocked_response.status_code = 200
        mocked_response.json.return_value = {"LinkList": {"Type": "Normal",
                                                          "Direction": "Source",
                                                          "Object": "Ticket",
                                                          "Key": "3"}}

        obj._parse_and_validate_response(mocked_response)
        self.assertEqual(obj._result_type, 'LinkList')
        self.assertDictEqual(obj.result, {"Type": "Normal",
                                                  "Direction": "Source",
                                                  "Object": "Ticket",
                                                  "Key": "3"})

    def test__validate_response_operation_link_list_empty(self):
        """Test _validate_response with link_list empty"""
        obj = Client(baseurl="http://localhost")
        obj.operation = "LinkList"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        mocked_response = mock.Mock(spec=requests.Response)
        mocked_response.status_code = 200
        mocked_response.json.return_value = {"LinkList": u''}

        obj._parse_and_validate_response(mocked_response)
        self.assertEqual(obj._result_type, 'LinkList')
        self.assertIsNone(obj.result)

    def test__validate_response_operation_ticket_get_error(self):
        """Test _validate_response with TicketGet when an error is received"""
        obj = Client(baseurl="http://localhost")
        obj.operation = "TicketGet"
        obj._result_type = obj.ws_config[obj.operation]["Result"]

        tkt = {"Error": {"ErrorMessage": "TicketGet: Authorization failing!",
                         "ErrorCode": "TicketGet.AuthFail"}}

        mocked_response = mock.Mock(spec=requests.Response)
        mocked_response.status_code = 200
        mocked_response.json.return_value = tkt

        self.assertRaisesRegex(APIError,
                               'Failed to access OTRS API. Check Username and Password.*',
                               obj._parse_and_validate_response,
                               mocked_response)


def main():
    unittest.main()


if __name__ == '__main__':
    main()

# EOF
