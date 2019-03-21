# -*- coding: utf-8 -*-
from __future__ import unicode_literals  # support both Python2 and 3

from doctest import DocTestSuite
from unittest import TestSuite


def load_tests(loader, tests, pattern):
    suite = TestSuite()
    suite.addTests(DocTestSuite('pyotrs.lib'))
    return suite
