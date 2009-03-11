##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
Test the ElementTree support within WebDAV. These aren't really tests but
more of an assertion that I spelt things, like variable names correctly. By
just calling the methods here I have managed to find a bunch of bugs. :-)

Otherwise I just assume that underlying engine does its job correctly.

$Id$
"""

import os
import os.path
import sys
import gc
import re
import unittest
from cStringIO import StringIO

from zope import component
from zope.testing import doctest
from zope.testing import renormalizing
from zope.testing import testrunner
from zope.interface.verify import verifyObject

import z3c.etree.etree
from interfaces import IEtree
from testing import etreeSetup, etreeTearDown


class BaseEtreeTestCase(unittest.TestCase):

    def test_interface(self):
        self.assertEqual(verifyObject(IEtree, self.etree), True)

    def test_comment(self):
        comment = self.etree.Comment(u"some text")

    def test_etree(self):
        etree = self.etree.ElementTree()

    def test_XML(self):
        xml = self.etree.XML(u"<p>some text</p>")

    def test_fromstring(self):
        xml = self.etree.fromstring(u"<p>some text</p>")

    def test_element(self):
        elem = self.etree.Element(u"testtag")

    def test_iselement(self):
        elem = self.etree.Element(u"testtag")
        iselem = self.etree.iselement(elem)
        self.assert_(iselem, "Not an element")

    def test_parse(self):
        f = StringIO("<b>Test Source String</b>")
        self.etree.parse(f)

    def test_qname(self):
        qname = self.etree.QName("http://example.namespace.org", "test")

    def test_tostring(self):
        elem = self.etree.Element(u"testtag")
        string = self.etree.tostring(elem, "ascii")
        self.assert_(isinstance(string, str), "Not a string")

    def test_treeBuilder(self):
        self.assertRaises(NotImplementedError, self.etree.TreeBuilder)

    def test_subelement(self):
        elem = self.etree.Element(u"testtag")
        subel = self.etree.SubElement(elem, "foo")

    def test_PI(self):
        pi = self.etree.PI("sometarget")

    def test_processinginstructions(self):
        pi = self.etree.ProcessingInstruction("sometarget")

    def test_xmltreebulider(self):
        builder = self.etree.XMLTreeBuilder()


class OrigElementTreeTestCase(BaseEtreeTestCase):

    def setUp(self):
        from z3c.etree.etree import EtreeEtree
        self.etree = EtreeEtree()

    def tearDown(self):
        del self.etree


class CElementTreeTestCase(BaseEtreeTestCase):

    def setUp(self):
        from z3c.etree.etree import CEtree
        self.etree = CEtree()

    def tearDown(self):
        del self.etree


class LXMLElementTreeTestCase(BaseEtreeTestCase):

    def setUp(self):
        from z3c.etree.etree import LxmlEtree
        self.etree = LxmlEtree()

    def tearDown(self):
        del self.etree

    def test_PI(self):
        self.assertRaises(NotImplementedError, self.etree.PI, "sometarget")

    def test_processinginstructions(self):
        self.assertRaises(NotImplementedError,
                          self.etree.ProcessingInstruction, "sometarget")

    def test_xmltreebulider(self):
        self.assertRaises(NotImplementedError, self.etree.XMLTreeBuilder)


class Python25ElementTreeTestCase(BaseEtreeTestCase):

    def setUp(self):
        from z3c.etree.etree import EtreePy25
        self.etree = EtreePy25()

    def tearDown(self):
        del self.etree


class NoElementTreePresentTestCase(unittest.TestCase):
    # If no element tree engine exists then run this test case. Which will
    # mark the current instance has broken.

    def test_warn(self):
        self.fail("""
        WARNING: z3c.etree needs ElementTree installed in order to run.
        """)


class setUp(object):

    def __init__(self, etree):
        self.etree = etree

    def __call__(self, test):
        component.getGlobalSiteManager().registerUtility(
            self.etree, provided = IEtree)
        test.globs["etree"] = self.etree


def tearDown(test):
    component.getGlobalSiteManager().unregisterUtility(
        test.globs["etree"], provided = IEtree)
    del test.globs["etree"]


checker = renormalizing.RENormalizing([
    # 2.5 changed the way pdb reports exceptions
        (re.compile(r"<class 'exceptions.(\w+)Error'>:"),
                    r'exceptions.\1Error:'),

        (re.compile('^> [^\n]+->None$', re.M), '> ...->None'),
        (re.compile("'[A-Z]:\\\\"), "'"), # hopefully, we'll make Windows happy
        (re.compile(r'\\\\'), '/'), # more Windows happiness
        (re.compile(r'\\'), '/'), # even more Windows happiness
       (re.compile('/r'), '\\\\r'), # undo damage from previous
       (re.compile(r'\r'), '\\\\r\n'),
       (re.compile(r'\d+[.]\d\d\d seconds'), 'N.NNN seconds'),
       (re.compile(r'\d+[.]\d\d\d ms'), 'N.NNN ms'),
        (re.compile('( |")[^\n]+doctest'), r'\1doctest'),
        (re.compile('( |")[^\n]+testrunner.py'), r'\1testrunner.py'),
        (re.compile(r'> [^\n]*(doc|unit)test[.]py\(\d+\)'),
                    r'\1doctest.py(NNN)'),
        (re.compile(r'[.]py\(\d+\)'), r'.py(NNN)'),
        (re.compile(r'[.]py:\d+'), r'.py:NNN'),
        (re.compile(r' line \d+,', re.IGNORECASE), r' Line NNN,'),

        # omit traceback entries for unittest.py or doctest.py from
        # output:
        (re.compile(r'^ +File "[^\n]+(doc|unit)test.py", [^\n]+\n[^\n]+\n',
                    re.MULTILINE),
         r''),
        (re.compile('^> [^\n]+->None$', re.M), '> ...->None'),
        (re.compile('import pdb; pdb'), 'Pdb()'), # Py 2.3

        # Omit the number of tests ran
        (re.compile(r'Ran \d+ tests with \d+ failures and \d+ errors'),
                    r'Ran N tests with N failures and N errors'),
        ])


class doctestsSetup(object):

    def __init__(self, engine_key):
        self.engine_key = engine_key

    def __call__(self, test):
        test.globs['saved-sys-info'] = (
            sys.path[:],
            sys.argv[:],
            sys.modules.copy(),
            gc.get_threshold(),
            )
        test.globs['this_directory'] = os.path.split(__file__)[0]
        test.globs['testrunner_script'] = __file__
        try:
            test.globs['old_configure_logging'] = testrunner.configure_logging
            testrunner.configure_logging = lambda : None
        except AttributeError:
            pass
        test.globs['old_engine'] = os.environ.get(
            z3c.etree.testing.engine_env_key)
        os.environ[z3c.etree.testing.engine_env_key] = self.engine_key


def doctestsTearDown(test):
    sys.path[:], sys.argv[:] = test.globs['saved-sys-info'][:2]
    gc.set_threshold(*test.globs['saved-sys-info'][3])
    sys.modules.clear()
    sys.modules.update(test.globs['saved-sys-info'][2])
    try:
        testrunner.configure_logging = test.globs['old_configure_logging']
        del test.globs['old_configure_logging']
    except KeyError:
        pass
    del os.environ[z3c.etree.testing.engine_env_key]
    del test.globs['old_engine']


class UnusedEtree(unittest.TestCase):

    def setUp(self):
        etreeSetup()

    def tearDown(self):
        etreeTearDown()

    def test_simple(self):
        # Just run a simple test to make sure that the setup / teardown
        # works without errors.
        self.assertEqual(1, 1)


def test_suite():
    suite = unittest.TestSuite()

    # Only run the tests for each elementtree that is installed.
    foundetree = False
    try:
        import elementtree
        suite.addTest(unittest.makeSuite(OrigElementTreeTestCase))
        suite.addTest(doctest.DocTestSuite(
            "z3c.etree.testing",
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = setUp(z3c.etree.etree.EtreeEtree()),
            tearDown = tearDown))
        suite.addTest(doctest.DocFileSuite(
            "doctesttests.txt", package = z3c.etree,
            checker = checker,
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = doctestsSetup("elementtree"),
            tearDown = doctestsTearDown))
        suite.addTest(doctest.DocFileSuite(
            "doctestssuccess.txt", package = z3c.etree,
            checker = z3c.etree.testing.xmlOutputChecker,
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = setUp(z3c.etree.etree.EtreeEtree()),
            tearDown = tearDown))
        suite.addTest(doctest.DocTestSuite(
            "z3c.etree.testing",
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = setUp(elementtree.ElementTree),
            tearDown = tearDown))
        suite.addTest(doctest.DocFileSuite(
            "doctestssuccess.txt", package = z3c.etree,
            checker = z3c.etree.testing.xmlOutputChecker,
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = setUp(elementtree.ElementTree),
            tearDown = tearDown))
        suite.addTest(doctest.DocFileSuite(
            "README.txt", package = z3c.etree,
            setUp = doctestsSetup("elementtree"),
            tearDown = doctestsTearDown))
        foundetree = True
    except ImportError:
        pass

    try:
        import cElementTree
        suite.addTest(unittest.makeSuite(CElementTreeTestCase))
        suite.addTest(doctest.DocTestSuite(
            "z3c.etree.testing",
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = setUp(z3c.etree.etree.CEtree()),
            tearDown = tearDown))
        suite.addTest(doctest.DocFileSuite(
            "doctesttests.txt", package = z3c.etree,
            checker = checker,
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = doctestsSetup("cElementTree"),
            tearDown = doctestsTearDown))
        suite.addTest(doctest.DocFileSuite(
            "doctestssuccess.txt", package = z3c.etree,
            checker = z3c.etree.testing.xmlOutputChecker,
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = setUp(z3c.etree.etree.CEtree()),
            tearDown = tearDown))
        suite.addTest(doctest.DocTestSuite(
            "z3c.etree.testing",
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = setUp(cElementTree),
            tearDown = tearDown))
        suite.addTest(doctest.DocFileSuite(
            "doctestssuccess.txt", package = z3c.etree,
            checker = z3c.etree.testing.xmlOutputChecker,
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = setUp(cElementTree),
            tearDown = tearDown))
        suite.addTest(doctest.DocFileSuite(
            "README.txt", package = z3c.etree,
            setUp = doctestsSetup("cElementTree"),
            tearDown = doctestsTearDown))
        foundetree = True
    except ImportError:
        pass

    try:
        import lxml.etree
        suite.addTest(unittest.makeSuite(LXMLElementTreeTestCase))
        suite.addTest(doctest.DocTestSuite(
            "z3c.etree.testing",
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = setUp(z3c.etree.etree.LxmlEtree()),
            tearDown = tearDown))
        suite.addTest(doctest.DocFileSuite(
            "doctesttests.txt", package = z3c.etree,
            checker = checker,
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = doctestsSetup("lxml"),
            tearDown = doctestsTearDown))
        suite.addTest(doctest.DocFileSuite(
            "doctestssuccess.txt", package = z3c.etree,
            checker = z3c.etree.testing.xmlOutputChecker,
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = setUp(z3c.etree.etree.LxmlEtree()),
            tearDown = tearDown))
        suite.addTest(doctest.DocTestSuite(
            "z3c.etree.testing",
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = setUp(lxml.etree),
            tearDown = tearDown))
        suite.addTest(doctest.DocFileSuite(
            "doctestssuccess.txt", package = z3c.etree,
            checker = z3c.etree.testing.xmlOutputChecker,
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = setUp(lxml.etree),
            tearDown = tearDown))
        suite.addTest(doctest.DocFileSuite(
            "README.txt", package = z3c.etree,
            setUp = doctestsSetup("lxml"),
            tearDown = doctestsTearDown))
        foundetree = True
    except ImportError:
        pass

    try:
        import xml.etree
        suite.addTest(unittest.makeSuite(Python25ElementTreeTestCase))
        suite.addTest(doctest.DocTestSuite(
            "z3c.etree.testing",
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = setUp(z3c.etree.etree.EtreePy25()),
            tearDown = tearDown))
        suite.addTest(doctest.DocFileSuite(
            "doctesttests.txt", package = z3c.etree,
            checker = checker,
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = doctestsSetup("py25"),
            tearDown = doctestsTearDown))
        suite.addTest(doctest.DocFileSuite(
            "doctestssuccess.txt", package = z3c.etree,
            checker = z3c.etree.testing.xmlOutputChecker,
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = setUp(z3c.etree.etree.EtreePy25()),
            tearDown = tearDown))
        suite.addTest(doctest.DocFileSuite(
            "README.txt", package = z3c.etree,
            setUp = doctestsSetup("py25"),
            tearDown = doctestsTearDown))
        foundetree = True
    except ImportError:
        pass

    if not foundetree:
        suite.addTest(unittest.makeSuite(NoElementTreePresentTestCase))
    else:
        # rerun the current testing doctest using the default setUp
        suite.addTest(doctest.DocTestSuite(
            "z3c.etree.testing",
            optionflags = doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE,
            setUp = etreeSetup,
            tearDown = etreeTearDown))

        # run the README tests to make the documentation does something
        suite.addTest(doctest.DocFileSuite(
            "README.txt", package = "z3c.etree"))

        # test teardown
        suite.addTest(unittest.makeSuite(UnusedEtree))

    return suite
