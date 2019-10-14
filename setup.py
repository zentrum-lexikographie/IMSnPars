#!/usr/bin/env python

from distutils.core import setup

setup(name='imsnpars',
      version='0.1.0',
      description='IMS neural Dependency Parser',
      author='AgnieszkaFalenska',
      author_email='',
      packages=[],
      entry_points={
          'console_scripts': [
              'imsnpars = main:main',
          ],
      }
)
