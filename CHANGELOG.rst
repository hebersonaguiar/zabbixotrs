Change Log
==========

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

[Unreleased]
------------
- add attachment load from file
- add attachment save to folder


1.0.0 - planned first release
-----------------------------

0.2.x - 2018-xx-yy (unreleased)
--------------------------------


0.3.0 - 2018-10-07
------------------
- internal: Update build and test tooling

0.2.4 - 2018-10-07
------------------
- fix bug in Client.__init() - Default Connector Config was always used

0.2.3 - 2018-08-21
------------------
- add "webservice_path" to Client() to allow custom path

0.1.29 - 2017-10-03
-------------------
- fix missing TicketID in Client.ticket_update()
- complete test coverage

0.1.28 - 2017-07-25
-------------------
- add option to set a User Agent for HTTP requests

0.1.27 - 2017-07-13
-------------------
- fix #11: Attachment.create_from_file fails on binary file

0.1.26 - 2017-07-12
-------------------
- fix #9: Add Type/TypeID to Ticket.create_basic()
- fix #10: hardcoded operation "TicketGetList" in Client.ticket_get_by_id()

0.1.25 - 2017-06-22
-------------------

0.1.24 - 2017-05-23
-------------------
- fix #8: Article handling in Client.ticket_create()

0.1.23 - 2017-05-17
-------------------
- add store attachment feature to cli

0.1.22 - 2017-03-04
-------------------
- completed FAQ API

0.1.21 - 2016-11-14
-------------------
- FAQ api not yet completed
- updated unittests for FAQ api (as far as implemented)
- fixed CLI client (webservice removed)

0.1.19 - 2016-11-12
-------------------
- ticket_search - dynamic_fields takes either a DynamicField to a list of DynamicFields
- BREAKING: implement FAQ api

0.1.18 - 2016-11-06
-------------------
- ticket_search will now return [] for empty result

0.1.17 - 2016-11-06
-------------------
- change name of lists (e.g. list_dynamic_fields is now dynamic_fields)
- update to_dct() method (add flags to choose what to print)

0.1.16 - 2016-11-05
-------------------
- fix bug when https_verify is disabled
- add link api
- add dynamic_field_get access
- add article_get access
- add `dynamic_fields` to ticket_search

0.1.9 - 2016-09-11
------------------
- full text search was fixed upstream and is now in beta testing

0.1.7 - 2016-04-24
------------------
- fix PyOTRS Shell CLI

0.1.6 - 2016-04-24
------------------
- fix some docs
- first upload to public repo
- added ticket_get_by_ids to get multiple tickets in one request
- completed full unittest coverage
- added Gitlab config for Continuous Integration testing
- Client.ticket_create() - create a Ticket in OTRS
- Setuptools for proper packaging

0.1.0 - 2016-04-10
------------------
- Initial creation
