=========
z3c.etree
=========

*z3c.etree* provides some mechanisms (a common interface) for integrating any
ElementTree engine with the Zope component architecture. This allows
applications to look up a engine against this interface. As such this package
does not implement the ElementTree API.

*z3c.etree* also provides a set of utilities that can be used to make
testing XML output in doctests easier. This functionality can also be called
from a python based unit test via the *assertXMLEqual* method.

Developers
==========

  >>> import z3c.etree
  >>> import z3c.etree.testing
  >>> engine = z3c.etree.testing.etreeSetup()

Here are some examples for how to use *z3c.etree* with your own code.

To generate a Element object with the tag *DAV:getcontenttype* all we have
to do is:

  >>> etree = z3c.etree.getEngine()
  >>> elem = etree.Element("{DAV:}getcontenttype")
  >>> elem #doctest:+ELLIPSIS
  <Element ...>
  >>> z3c.etree.testing.assertXMLEqual(etree.tostring(elem), """
  ...    <getcontenttype xmlns="DAV:"/>""")

Now to add a value this element use just use the *elem* variable has the API
suggests.

  >>> elem.text = "text/plain"
  >>> z3c.etree.testing.assertXMLEqual(etree.tostring(elem), """
  ...    <getcontenttype xmlns="DAV:">text/plain</getcontenttype>""")

Tear-down
=========

  >>> z3c.etree.testing.etreeTearDown()
