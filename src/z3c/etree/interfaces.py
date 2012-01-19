##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
Zope Element Tree Support
"""

from zope import interface

class IEtree(interface.Interface):

    def Comment(text = None):
        """
        """

    def dump(elem):
        """
        """

    def Element(tag, attrib = {}, **extra):
        """
        """

    def ElementTree(element = None, file = None):
        """
        """

    def XML(text):
        """
        """

    def fromstring(text):
        """
        """

    def iselement(element):
        """
        """

    def iterparse(source, events = None):
        """
        """

    def parse(source, parser = None):
        """
        """

    def PI(target, text = None):
        """
        """

    def ProcessingInstruction(target, text = None):
        """
        """

    def QName(text_or_uri, tag = None):
        """
        """

    def SubElement(parent, tag, attrib = {}, **extra):
        """
        """

    def tostring(element, encoding = None):
        """
        """

    def TreeBuilder(element_factory = None):
        """
        """

    def XMLTreeBuilder(html = 0, target = None):
        """
        """
