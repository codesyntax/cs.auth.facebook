from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='cs.auth.facebook',
      version=version,
      description="Facebook authentication plugin for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone pas login facebook authentication',
      author='Mikel Larreategi',
      author_email='',
      url='http://github.com/codesyntax/cs.auth.facebook',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['cs', 'cs.auth'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.interface',
          'zope.publisher',
          'zope.i18nmessageid',
          'five.globalrequest',
          'collective.beaker',
          'Products.PluggableAuthService',
          'Products.PlonePAS',
          'Products.statusmessages',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
