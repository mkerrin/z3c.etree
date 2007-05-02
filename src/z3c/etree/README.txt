=========================
Zope Element Tree Support
=========================

This package does not implement the ElementTree API but instead provides
proxy objects that wrap some of the more common ElementTree implementations.
Then one of these proxy objects is registered as a utility, providing the
*z3c.etree.interfaces.IEtree* interface, which can be looked up through
the Zope component architecture. Thus removing the hard dependency a Python
import statement introduces on any one ElementTree implementation.

This will allow anyone interested in just trying out a module developed using
*z3c.etree* to use a pure Python implementation of ElementTree (which is really
easy to install, but slow). While a developer who is in the final stages of
going live with a new site might want to configure the same module to use lxml
(which is *not* easy to install as it depends on libxml2 and libxslt but is
really, really, really fast).

If there is any ElementTree implementation that I have missed, or any bugs,
improvements, then please contact me at
michael.kerrin@openapp.ie and I will do my best to fix the situation.

Installation and Configuration
==============================

*z3c.etree* is installed like any other Zope3 module. That is it should be
copied verbatim into your Python path and the z3c.etree-configure.zcml file
should be copied to the package-includes directory for each instance of Zope
that requires this package. (Once I figure out how to, I will use Python eggs
for the installation process.)

Now each of the z3c.etree-configure.zcml files that exist in a instances
package-includes directory can be edited to configure which ElementTree
implementation to use within that instance.

To configure a particular ElementTree implementation for an instance the
z3c.etree-configure.zcml file should contain only one ZCML utility
declaration. For example to configure an instance use lxml
z3c.etree-configure.zcml should contain the the following::

  <utility
     factory="z3c.etree.etree.LxmlEtree"
     />

Where *z3c.etree.etree.LxmlEtree* is the proxy object that wraps the lxml
implementation. Currently the other implementations include:

+ *z3c.etree.etree.EtreeEtree* - proxy for the pure python *elementtree*
  module.

+ *z3c.etree.etree.EtreePy25* - proxy for the ElementTree implementation
  included in Python 2.5's standard library.

Tests setup
===========

Some setup for the developers tests.

  >>> from zope import component
  >>> import z3c.etree.interfaces

This happens automatically during Zope startup.

  >>> from z3c.etree.testing import etreeSetup, etreeTearDown
  >>> from z3c.etree.testing import assertXMLEqual
  >>> dummy = etreeSetup()

Developers
==========

Here are some examples for how to use *z3c.etree* with your own code.

To generate a Element object with the tag *DAV:getcontenttype* all we have
to do is:

  >>> etree = component.getUtility(z3c.etree.interfaces.IEtree)
  >>> elem = etree.Element("{DAV:}getcontenttype")
  >>> assertXMLEqual(etree.tostring(elem), """
  ...    <ns0:getcontenttype xmlns:ns0="DAV:"/>""")

Now to add a value this element use just use the *elem* variable has the API
suggests.

  >>> elem.text = "text/plain"
  >>> assertXMLEqual(etree.tostring(elem), """
  ...    <ns0:getcontenttype xmlns:ns0="DAV:">text/plain</ns0:getcontenttype>""")

Testing
=======

For developers who are writing unit tests for their code that uses
*z3c.etree*. They should call the method *z3c.etree.testing.etreeSetup* in
there tests setup code, in order to correctly register a ElementTree utility
for use within their tests. And similar, call the method
*z3c.etree.testing.etreeTearDown* in their teardown code. See the Setup
and Teardown sections of this file.

The *etreeSetup* method will load and parse the *z3c.etree-configure.zcml*
file from within the *z3c.etree* module (NOT the file from the instance). So
if the default utility defined in this file, which is
*z3c.etree.etree.EtreeEtree*, doesn't apply to your system due to a missing
module for example, then this file should be edited to reflect this.

Teardown
========

  >>> etreeTearDown()
