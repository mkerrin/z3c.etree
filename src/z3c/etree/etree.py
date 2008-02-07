##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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

import copy
from zope.interface import implements

from interfaces import IEtree

class BaseEtree(object):
    def Comment(self, text = None):
        return self.etree.Comment(text)

    # XXX - not tested
    def dump(self, elem):
        return self.etree.dump(elem)

    def Element(self, tag, attrib = {}, **extra):
        return self.etree.Element(tag, attrib, **extra)

    def ElementTree(self, element = None, file = None):
        return self.etree.ElementTree(element, file = file)

    def XML(self, text):
        return self.etree.fromstring(text)

    fromstring = XML

    def iselement(self, element):
        return self.etree.iselement(element)

    # XXX - not tested
    def iterparse(self, source, events = None):
        return self.etree.iterparse(source, events)

    def parse(self, source, parser = None):
        return self.etree.parse(source, parser)

    def PI(self, target, text = None):
        raise NotImplementedError, "lxml doesn't implement PI"

    ProcessingInstruction = PI

    def QName(self, text_or_uri, tag = None):
        return self.etree.QName(text_or_uri, tag)

    def SubElement(self, parent, tag, attrib = {}, **extra):
        return self.etree.SubElement(parent, tag, attrib, **extra)

    def tostring(self, element, encoding = None):
        return self.etree.tostring(element, encoding = encoding)

    def TreeBuilder(self, element_factory = None):
        raise NotImplementedError, "lxml doesn't implement TreeBuilder"

    def XMLTreeBuilder(self, html = 0, target = None):
        raise NotImplementedError, "lxml doesn't implement XMLTreeBuilder"


class EtreeEtree(BaseEtree):
    implements(IEtree)

    def __init__(self):
        from elementtree import ElementTree
        self.etree = ElementTree

    def XMLTreeBuilder(self, html = 0, target = None):
        return self.etree.XMLTreeBuilder(html, target)

    def PI(self, target, text = None):
        return self.etree.PI(target, text)

    ProcessingInstruction = PI


class CEtree(EtreeEtree):
    implements(IEtree)

    def __init__(self):
        import cElementTree
        self.etree = cElementTree


class EtreePy25(BaseEtree):
    implements(IEtree)

    def __init__(self):
        from xml.etree import ElementTree
        self.etree = ElementTree

    def XMLTreeBuilder(self, html = 0, target = None):
        return self.etree.XMLTreeBuilder(html, target)

    def PI(self, target, text = None):
        return self.etree.PI(target, text)

    ProcessingInstruction = PI


class LxmlEtree(BaseEtree):
    implements(IEtree)

    def __init__(self):
        from lxml import etree
        self.etree = etree
