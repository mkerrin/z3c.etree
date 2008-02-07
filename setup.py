from setuptools import setup, find_packages

setup(name = "z3c.etree",
      version = "0.9.2",
      author = "Michael Kerrin",
      author_email = "michael.kerrin@openapp.ie",
      url = "http://svn.zope.org/z3c.etree",
      description = "Abstracts out the implementation of elementtree " \
                    "behind the zope component architecture. And provides " \
                    "helper functions for testing XML output in tests.",
      long_description = (
          open("src/z3c/etree/README.txt").read() +
          "\n\n" +
          open("CHANGES.txt").read()),
      license = "ZPL",
      classifiers = ["Topic :: Software Development :: Testing",
                     "Intended Audience :: Developers",
                     "License :: OSI Approved :: Zope Public License",
                     "Programming Language :: Python",
                     "Framework :: Zope3",
                     ],

      packages = find_packages("src"),
      package_dir = {"": "src"},
      install_requires = ["setuptools"],
      extras_require = dict(test = ["zope.app.testing",
                                    "elementtree",
                                    "cElementTree",
                                    "lxml"]),

      include_package_data = True,
      test_suite='z3c.etree.tests.test_suite',
      zip_safe = False)
