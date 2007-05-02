import unittest
from zope.testing import doctest
import zope.etree.testing


def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(doctest.DocFileSuite(
        "doctests.txt",
        checker = zope.etree.testing.xmlOutputChecker,
        setUp = zope.etree.testing.etreeSetup,
        tearDown = zope.etree.testing.etreeTearDown,
        optionflags = zope.etree.testing.XMLDATA))

    return suite
