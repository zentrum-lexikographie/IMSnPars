#!/usr/bin/env python

from distutils.core import setup

setup(name='imsnpars',
      version='0.1.0',
      description=' IMS Neural Dependency Parser',
      author='Agnieszka Faleńska',
      author_email='agnieszka.falenska@ims.uni-stuttgart.de',
      packages=['imsnpars'],
      install_requires=[
          'dynet @ git+https://github.com/clab/dynet#egg=dynet',
          'networkx'
      ],
      entry_points={
          'console_scripts': [
              'imsnpars = imsnpars.main:main',
          ],
      }
)
