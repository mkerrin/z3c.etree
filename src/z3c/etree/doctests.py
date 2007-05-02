import unittest
from zope.testing import doctest
import z3c.etree.testing


def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(doctest.DocFileSuite(
        "doctests.txt",
        checker = z3c.etree.testing.xmlOutputChecker,
        setUp = z3c.etree.testing.etreeSetup,
        tearDown = z3c.etree.testing.etreeTearDown,
        optionflags = z3c.etree.testing.XMLDATA))

    return suite
