#!/usr/bin/env python3
from setuptools import find_packages, setup

from mope.__version__ import __version__
from mope.compat import PYTHON36

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = ['requests']
if PYTHON36:
    install_requires.append('dataclasses')

setup(
    name='python-mope',
    version=__version__,
    description='A client library for interacting with the Mopé Web Shop API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Lemuel Boyce',
    author_email='lemuel@vokality.com',
    packages=find_packages(exclude=["tests"]),
    url='https://github.com/rhymiz/python-mope',
    include_package_data=True,
    zip_safe=True,
    license='MIT',
    python_requires='>=3.6,<=3.10',
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
