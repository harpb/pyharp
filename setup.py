from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name = 'pyHarp',
      version = version,
      description = "Tools for python",
      long_description = """\
These set of tools...""",
      classifiers = [],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords = 'file, move, remove',
      author = 'HarpB',
      author_email = 'hi@harpb.com',
      url = 'https://github.com/harpb/pyharp',
      license = 'BSD',
      include_package_data = True,
      zip_safe = True,
      install_requires = [
          'django'
      ],
      packages =['pyharp'],
      )
