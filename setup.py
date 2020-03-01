#!/usr/bin/env python3
from setuptools import find_packages, setup

from mope.__version__ import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='python-mope',
      version=__version__,
      description='A client library for interacting with Mopé Web Shop APIs',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='Lemuel Boyce',
      author_email='lemuel@vokality.com',
      packages=find_packages(exclude=["tests"]),
      url='https://github.com/rhymiz/python-mope',
      include_package_data=True,
      zip_safe=False,
      license='MIT',
      python_requires='>=3.6',
      install_requires=[
          'requests'
      ],
      classifiers=[
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ])
