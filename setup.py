#!/usr/bin/env python


from setuptools import setup, find_packages

setup(name='imsnpars',
      version='0.1.0',
      description=' IMS Neural Dependency Parser',
      author='Agnieszka Faleńska',
      author_email='agnieszka.falenska@ims.uni-stuttgart.de',
      packages=find_packages(exclude=['tests']),
      install_requires=[
          'dynet @ git+https://github.com/clab/dynet@7c533e#egg=dynet',
          'networkx==2.4',
          'conllu==3.1.1',
          'Click==7.1.2'
      ],
      extras_require={
          'test': [
              'pytest'
          ]
      },
      entry_points={
          'console_scripts': [
              'imsnpars = imsnpars.main:main',
              'imsnpars-parse = imsnpars.cli:main',
          ],
      }
)
