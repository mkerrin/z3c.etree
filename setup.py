from setuptools import setup, find_packages

setup(name = "z3c.etree",
      version = "0.9.1",
      author = "Michael Kerrin",
      author_email = "michael.kerrin@openapp.ie",
      url = "http://svn.zope.org/z3c.etree",
      description = "Abstracts out the the implementation of elementtree " \
                    "behind the zope component architecture",
      license = "ZPL",

      packages = find_packages("src"),
      package_dir = {"": "src"},
      install_requires = ["setuptools"],
      extras_require = dict(test = ["zope.app.testing",
                                    "elementtree",
                                    "cElementTree",
                                    "lxml"]),

      include_package_data = True,
      zip_safe = False)
