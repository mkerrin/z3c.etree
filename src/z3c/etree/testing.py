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
"""Zope Element Tree Support

$Id$
"""
__docformat__ = 'restructuredtext'

import os
import zope.component
from zope.testing import doctest

import z3c.etree
import z3c.etree.interfaces
import z3c.etree.etree

#
# Setup for Zope etree. 
#

engine_env_key = "ELEMENTTREE_ENGINE"

known_engines = {
    "cElementTree": "cElementTree",
    "elementtree": "elementtree.ElementTree",
    "lxml": "lxml.etree",
    "py25": "xml.etree.ElementTree",
    }


def importEngine(modname):
    components = modname.split(".")
    engine = __import__(modname)
    for comp in components[1:]:
        engine = getattr(engine, comp)
    return engine


def etreeSetup(test = None):
    engine = None

    if engine_env_key in os.environ:
        engine = importEngine(known_engines[os.environ[engine_env_key]])
    else:
        for key, modname in known_engines.items():
            try:
                engine = importEngine(modname)
                break
            except ImportError:
                pass

    if engine is None:
        raise ValueError("Failed to import a known element tree implementation")

    zope.component.getGlobalSiteManager().registerUtility(
        engine, provided = z3c.etree.interfaces.IEtree)

    if test is not None:
        test.globs["etree"] = engine
        test.globs["assertXMLEqual"] = assertXMLEqual

    # Sometimes during testing the placelesssetup method is used and this
    # tears down the global site manager during teardown. If the elementtree
    # engine was never used during the lifetime of the test then we get an
    # error in trying to teardown the engine. The getEngine method caches
    # the utility lookup bypassing the need for the global site manger
    # to know about the utility and thus not causing errors during tear down.
    engine = z3c.etree.getEngine()
    return engine


def etreeTearDown(test = None):
    etreeEngine = None
    if test is not None:
        etreeEngine = test.globs["etree"]
        del test.globs["etree"]
        del test.globs["assertXMLEqual"]
    if etreeEngine is None:
        etreeEngine = z3c.etree.getEngine()
    zope.component.getGlobalSiteManager().unregisterUtility(
        etreeEngine, provided = z3c.etree.interfaces.IEtree)
    z3c.etree._utility = None # clear the cache

#
# Handy methods for testing if two xml fragmenets are equal.
#

def _assertTextEqual(want, got, optionflags):
    """

    Equal values.

      >>> _assertTextEqual(None, "\\n", XMLDATA)
      (True, None)

      >>> _assertTextEqual(None, "\\n", XMLDATA)
      (True, None)

      >>> _assertTextEqual("\\n", None, XMLDATA)
      (True, None)

      >>> _assertTextEqual("\\n", "\\n", XMLDATA)
      (True, None)

      >>> _assertTextEqual("test", "test", XMLDATA)
      (True, None)

    Normalize Whitespace

      >>> _assertTextEqual("test\\nthis", "test this", 
      ...                  XMLDATA|doctest.NORMALIZE_WHITESPACE)
      (True, None)

    Ellipsis.

      >>> _assertTextEqual("test ...", "test 324324", 
      ...                  XMLDATA|doctest.ELLIPSIS)
      (True, None)

    Unequal values.

      >>> _assertTextEqual("test", None, XMLDATA)
      (False, "''test' != None' have different element content.")

      >>> _assertTextEqual(None, "test", XMLDATA)
      (False, "'None != 'test'' have different element content.")

      >>> _assertTextEqual("test", "nottest", XMLDATA)
      (False, "''test' != 'nottest'' have different element content.")

      >>> etree = z3c.etree.getEngine()
      >>> _assertTextEqual("test", etree.Element("test"), XMLDATA)
      Traceback (most recent call last):
      ...
      ValueError: _assertTextEqual can only tests text content

    """
    twant = isinstance(want, (str, unicode)) and want.strip()
    tgot = isinstance(got, (str, unicode)) and got.strip()

    if want is None:
        twant = ""

    if got is None:
        tgot = ""

    if not isinstance(twant, (str, unicode)) or \
           not isinstance(tgot, (str, unicode)):
        raise ValueError("_assertTextEqual can only tests text content")

    checker = doctest.OutputChecker()
    if checker.check_output(twant, tgot, optionflags):
        return True, None
    return False, "'%r != %r' have different element content." %(want, got)


def _assertSubXMLElements(want, got, optionflags):
    for index in range(0, len(want)):
        result, msg = _assertXMLElementEqual(
            want[index], got[index], optionflags)
        if not result:
            return result, msg

    return True, None


def _assertSubXMLElementsUnordered(want, got, optionflags):
    # First we check all the elements in order and if one of the elements
    # tags doesn't match what we expected then we start to call the `findall'
    # method to try and find the element we expected. The reason for this is
    # that if we do have multiple elements in an XML fragment with the same
    # tag it is very hard to report on which element didn't match which. But
    # in the case of WebDAV this works a treat since the ordering of
    # properties is depended on the Zope component architecture but we never
    # have multiple properties in these XML documents.
    for index in range(0, len(want)):
        wantchild = want[index]
        gotchild = got[index]
        if wantchild.tag != gotchild.tag:
            gotchild = got.findall(str(wantchild.tag))
            if len(gotchild) == 0:
                return False, \
                       "Failed to find the element %r in the fragment %r." %(
                           str(wantchild.tag), str(got.tag))
            if len(gotchild) > 1:
                return False, "Too many %r sub-elements where found in %r. " \
                              "Ordering algorithim broke down." %(
                    str(wantchild.tag), str(got.tag))
            gotchild = gotchild[0]
        result, msg = _assertXMLElementEqual(
            wantchild, gotchild, optionflags)
        if not result:
            return result, msg

    return True, None


def _assertXMLElementEqual(want, got, optionflags):
    # See assertXMLEqual for tests - it is easier to the tests with
    # strings that get converted to element tree objects in
    # assertXMLEqual.
    etree = z3c.etree.getEngine()

    if want.tag != got.tag:
        return False, "%r != %r different tag name." %(str(want.tag),
                                                       str(got.tag))
    if len(want) != len(got):
        return False, "%d != %d different number of subchildren on %r." %(
            len(want), len(got), want.tag)

    result, msg =_assertTextEqual(want.text, got.text, optionflags)
    if not result:
        return result, msg

    if (not (optionflags & XMLDATA_IGNOREMISSINGATTRIBUTES or
            optionflags & XMLDATA_IGNOREEXTRAATTRIBUTES)
        and len(want.attrib) != len(got.attrib)):
        return False, "%d != %d different number of attributes on %r." %(
            len(want.attrib), len(got.attrib), want.tag)

    for attrib, attrib_value in want.attrib.items():
        if attrib not in got.attrib:
            if not optionflags & XMLDATA_IGNOREMISSINGATTRIBUTES:
                return False, "%r expected to find the %r attribute." %(
                    want.tag, attrib)
        else:
            if got.attrib[attrib] != attrib_value:
                return False, (
                    "%r attribute has different value for the %r tag." % (
                        attrib, want.tag))

    for attrib, attrib_value in got.attrib.items():
        if attrib not in want.attrib:
            if not optionflags & XMLDATA_IGNOREEXTRAATTRIBUTES:
                return False, "%r found the unexpected %r attribute." %(
                    got.tag, attrib)

    if optionflags & XMLDATA_IGNOREORDER:
        return _assertSubXMLElementsUnordered(want, got, optionflags)
    else:
        return _assertSubXMLElements(want, got, optionflags)


def _cleanTree(want, got):
    etree = z3c.etree.getEngine()

    if isinstance(want, (str, unicode)):
        want = etree.fromstring(want)
    if isinstance(got, (str, unicode)):
        got = etree.fromstring(got)

    if getattr(want, "getroot", None) is not None:
        # Most then likely a ElementTree object.
        want = want.getroot()

    if getattr(got, "getroot", None) is not None:
        # Most then likely a ElementTree object.
        got = got.getroot()

    return want, got


def assertXMLEqual(want, got):
    """

      >>> assertXMLEqual('<test>xml</test>', '<test>xml</test>')

    Different element names. Element names are tested before attributes and
    number of children, and content.

      >>> assertXMLEqual('<test>XXX</test>', '<testx b="c">YYY</testx>')
      Traceback (most recent call last):
      ...
      AssertionError: 'test' != 'testx' different tag name.

    Different number of children. Number of children is tested before
    content.

      >>> assertXMLEqual('<test><subtest>Test</subtest></test>',
      ...                '<test>Sub-Test</test>')
      Traceback (most recent call last):
      ...
      AssertionError: 1 != 0 different number of subchildren on 'test'.

    Different element content.

      >>> assertXMLEqual('<test>xml</test>', '<test>xml1</test>')
      Traceback (most recent call last):
      ...
      AssertionError: ''xml' != 'xml1'' have different element content.

    Different number of attributes on a tag.

      >>> assertXMLEqual('<test b="c"/>', '<test/>')
      Traceback (most recent call last):
      ...
      AssertionError: 1 != 0 different number of attributes on 'test'.

    Different attribute content.

      >>> assertXMLEqual('<test b="c"/>', '<test b="d"/>')
      Traceback (most recent call last):
      ...
      AssertionError: 'b' attribute has different value for the 'test' tag.

    Different attributes.

      >>> assertXMLEqual('<test b="c"/>', '<test bb="d"/>')
      Traceback (most recent call last):
      ...
      AssertionError: 'test' expected to find the 'b' attribute.

    Attributes ok.

      >>> assertXMLEqual('<test b="c"/>', '<test b="c"/>')

    Subelement is wrong. Tests _assertXMLElementEqual recursion. First test
    subelement with different name.

      >>> assertXMLEqual('<test><subtest a="b"/></test>',
      ...    '<test><subtest1>Content</subtest1></test>')
      Traceback (most recent call last):
      ...
      AssertionError: 'subtest' != 'subtest1' different tag name.

    Test different number of elements on a sub element.
      
      >>> assertXMLEqual('<test><subtest>Content</subtest></test>',
      ...    '<test><subtest><subtest-2/></subtest></test>')
      Traceback (most recent call last):
      ...
      AssertionError: 0 != 1 different number of subchildren on 'subtest'.

    Different element content.

      >>> assertXMLEqual('<test><subtest>XXX</subtest></test>',
      ...    '<test><subtest>YYY</subtest></test>')
      Traceback (most recent call last):
      ...
      AssertionError: ''XXX' != 'YYY'' have different element content.

    Different number of attributes.

      >>> assertXMLEqual('<test><subtest a="b" c="d">XXX</subtest></test>',
      ...    '<test><subtest a="b">XXX</subtest></test>')
      Traceback (most recent call last):
      ...
      AssertionError: 2 != 1 different number of attributes on 'subtest'.

    Different attribute content on subelement.

      >>> assertXMLEqual('<test><subtest a="d">XXX</subtest></test>',
      ...    '<test><subtest a="b">XXX</subtest></test>')
      Traceback (most recent call last):
      ...
      AssertionError: 'a' attribute has different value for the 'subtest' tag.

    Missing attribute.

      >>> assertXMLEqual('<test><subtest attr="d">XXX</subtest></test>',
      ...    '<test><subtest a="b">XXX</subtest></test>')
      Traceback (most recent call last):
      ...
      AssertionError: 'subtest' expected to find the 'attr' attribute.

    Recursion ok.

      >>> assertXMLEqual('<test><subtest attr="d">XXX</subtest></test>',
      ...    '<test><subtest attr="d">XXX</subtest></test>')

    Whitespace doesn't matter.

      >>> assertXMLEqual('<test ><b><c /></b></test>',
      ...    '<test><b><c/></b></test>')

    Test passing elementtree objects through the first arguement.

      >>> etree = z3c.etree.getEngine()
      >>> elroot = etree.Element('test')
      >>> eltree = etree.ElementTree(elroot)

      >>> assertXMLEqual(eltree, '<test />')

      >>> assertXMLEqual(eltree, etree.ElementTree(etree.Element('test')))

      >>> assertXMLEqual(eltree, etree.Element('test'))

      >>> assertXMLEqual(elroot, '<test />')

    """
    want, got = _cleanTree(want, got)

    result, msg = _assertXMLElementEqual(want, got, XMLDATA)
    assert result, msg


def assertXMLEqualIgnoreOrdering(want, got):
    """

      >>> assertXMLEqualIgnoreOrdering('<test>xml</test>', '<test>xml</test>')

    Re-ording sub-elements of an XML fragment still passes with this method.

      >>> assertXMLEqualIgnoreOrdering(
      ...    '<test><a>Content</a><b>Content</b></test>',
      ...    '<test><a>Content</a><b>Content</b></test>')

    Now we re-order the `a' and `b' elements.

      >>> assertXMLEqualIgnoreOrdering(
      ...    '<test><a>Content</a><b>Content</b></test>',
      ...    '<test><b>Content</b><a>Content</a></test>')

    But with the previous `assertXMLEqual' it still fails.

      >>> assertXMLEqual(
      ...    '<test><a>Content</a><b>Content</b></test>',
      ...    '<test><b>Content</b><a>Content</a></test>')
      Traceback (most recent call last):
      ...
      AssertionError: 'a' != 'b' different tag name.

    Ording still picks up on different attributes.

      >>> assertXMLEqualIgnoreOrdering(
      ...    '<test><a attr="1">Content</a><b>Content</b></test>',
      ...    '<test><b>Content</b><a>Content</a></test>')
      Traceback (most recent call last):
      ...
      AssertionError: 1 != 0 different number of attributes on 'a'.

    And on different content.

      >>> assertXMLEqualIgnoreOrdering(
      ...    '<test><a>Different content</a><b>Content</b></test>',
      ...    '<test><b>Content</b><a>Content</a></test>')
      Traceback (most recent call last):
      ...
      AssertionError: ''Different content' != 'Content'' have different element content.

    Missing element.

      >>> assertXMLEqualIgnoreOrdering(
      ...    '<test><b>Content</b></test>',
      ...    '<test><b>Content</b><a>Content</a></test>')
      Traceback (most recent call last):
      ...
      AssertionError: 1 != 2 different number of subchildren on 'test'.

      >>> assertXMLEqualIgnoreOrdering(
      ...    '<test><c>Content</c><b>Content</b></test>',
      ...    '<test><b>Content</b><a>Content</a></test>')
      Traceback (most recent call last):
      ...
      AssertionError: Failed to find the element 'c' in the fragment 'test'.

    Un-ordering matching does not work when we have more then one sub-element
    with the same tag. This is problematic as their is no way for me to find
    the correct expected element reliably.

      >>> assertXMLEqualIgnoreOrdering(
      ...    '<test><a>Content</a><b>Content</b><a>Test</a></test>',
      ...    '<test><b>Content</b><a>Content</a><a>Test</a></test>')
      Traceback (most recent call last):
      ...
      AssertionError: Too many 'a' sub-elements where found in 'test'. Ordering algorithim broke down.

    But if the ordering breaks down within a level of the XML fragment that
    doesn't contain duplicate elements then everything works. Even though we
    have duplicate `r' elements it is only on the third level that the sub
    ordering breaks down and so the documents match.

      >>> assertXMLEqualIgnoreOrdering(
      ...  '<test><r><a>Content</a><b>Content</b></r><r><a>Test</a></r></test>',
      ...  '<test><r><b>Content</b><a>Content</a></r><r><a>Test</a></r></test>')

      >>> etree = z3c.etree.getEngine()

    Pass `assertXMLEqualIgnoreOrdering' an actual elementtree element object
    whose tag was setup via the etree.QName method. Make sure that we don't
    have any errors in processing this element.

      >>> el = etree.Element('test')
      >>> el.append(etree.Element(etree.QName('testns:', 'a')))
      >>> el[-1].text = 'Content'
      >>> el.append(etree.Element('{testns:}b'))
      >>> el[-1].text = 'Content'

      >>> assertXMLEqualIgnoreOrdering(el,
      ...  '<test><b xmlns="testns:">Content</b><a xmlns="testns:">Content</a></test>')

      >>> assertXMLEqualIgnoreOrdering(
      ...  '<test><b xmlns="testns:">Content</b><a xmlns="testns:">Content</a></test>',
      ...  el)

    Also make sure that the errors messages returned by
    `assertXMLEqualIgnoreOrdering' when we have a QName tag are readable.

      >>> assertXMLEqualIgnoreOrdering(
      ...  '<test><b>Content</b><a>Content</a></test>',
      ...  el)
      Traceback (most recent call last):
      ...
      AssertionError: Failed to find the element 'b' in the fragment 'test'.

      >>> assertXMLEqualIgnoreOrdering(el,
      ...  '<test><b>Content</b><a>Content</a></test>')
      Traceback (most recent call last):
      ...
      AssertionError: Failed to find the element '{testns:}a' in the fragment 'test'.

    Finally - test passing elementtree objects through the first arguement.

      >>> elroot = etree.Element('test')
      >>> eltree = etree.ElementTree(elroot)

      >>> assertXMLEqual(eltree, '<test />')

      >>> assertXMLEqual(eltree, etree.ElementTree(etree.Element('test')))

      >>> assertXMLEqual(eltree, etree.Element('test'))

      >>> assertXMLEqual(elroot, '<test />')

    """
    want, got = _cleanTree(want, got)

    result, msg = _assertXMLElementEqual(want, got, XMLDATA_IGNOREORDER)
    assert result, msg

#
# Integrate the above methods with doctest.
#

def _assertXMLElement(want, got, optionflags):
    etree = z3c.etree.getEngine()

    def clean_string(s):
        if not isinstance(s, (str, unicode)):
            return s # not tested
        s = s.strip()
        if s[0] in ("'", '"') and s[-1] in ("'", '"'):
            s = s[1:-1]
        return s

    want = etree.fromstring(clean_string(want))
    got = etree.fromstring(clean_string(got))

    return _assertXMLElementEqual(want, got, optionflags)


XMLDATA = doctest.register_optionflag("XMLDATA")

XMLDATA_IGNOREORDER = doctest.register_optionflag("XMLDATA_IGNOREORDER")

XMLDATA_IGNOREMISSINGATTRIBUTES = doctest.register_optionflag(
    "XMLDATA_IGNOREMISSINGATTRIBUTES")

XMLDATA_IGNOREEXTRAATTRIBUTES = doctest.register_optionflag(
    "XMLDATA_IGNOREEXTRAATTRIBUTES")

class XMLOutputChecker(doctest.OutputChecker):

    def check_output(self, want, got, optionflags):
        if optionflags & XMLDATA or optionflags & XMLDATA_IGNOREORDER:
            if want and got: # it only makes sense to compare actual data.
                result, msg = _assertXMLElement(want, got, optionflags)
                return result
        return doctest.OutputChecker.check_output(
            self, want, got, optionflags)

    def output_difference(self, example, got, optionflags):
        if optionflags & XMLDATA or optionflags & XMLDATA_IGNOREORDER:
            want = example.want
            if want and got: # it only makes sense to compare actual data
                error = 'Expected:\n%sGot:\n%s' %(doctest._indent(want),
                                                  doctest._indent(got))
                result, errmsg = _assertXMLElement(want, got, optionflags)
                assert not result, "assertXMLEqual didn't fail."

                if errmsg:
                    error += "XML differences:\n" + \
                                 doctest._indent(errmsg) + "\n"
                else: # XXX - not tested
                    error += "No known XML difference."

                return error
        # XXX - not tested
        return doctest.OutputChecker.output_difference(
            self, example, got, optionflags)

xmlOutputChecker = XMLOutputChecker()

__all__ = ("etreeSetup", "etreeTearDown",
           "xmlOutputChecker", "assertXMLEqual", "XMLDATA",
           "assertXMLEqualIgnoreOrdering", "XMLDATA_IGNOREORDER")
