"""
Libchickadee Overview
=====================

Yet another GeoIP resolution tool.

Libchickadee is a library consisting of tools to extract IP addresses from
files, resolve the IP address information using third-party data sources, and
present the resolutions to the end-user in an easy to consume manner. While the
library consists all of these components, it is primarily leveraged by a single
command line utility, ``chickadee``. The library components can be called
outside of the ``chickadee`` utility and this documentation provides
information on using the library in addition to the command line tool.

.. _installation:

Installation
------------

You may install Chickadee on your platform using ``pip install chickadee`` (you
may need to use ``pip3`` depending on your system configuration).
**Please ensure you are using Python 3**

You may also install via the source code as detailed below.

macOS and Linux
^^^^^^^^^^^^^^^

Requirements:

* Python 3+, installed on your path
* Virtualenv (``pip3 install virtualenv``)

#. Clone the git repo: ``git clone https://github.com/chapinb/chickadee.git``
#. Create your virtual environment ``virtualenv -p python3 venv3`` and
   activate it (``source venv3/bin/activate``)
#. Install dependencies: ``pip install .``
#. Run ``chickadee --help`` to get started.

Windows
^^^^^^^

Requirements:

* Python 3+, installed on your path
* Virtualenv (``pip.exe install virtualenv``)

#. Clone the git repo: ``git clone https://github.com/chapinb/chickadee.git``
#. Create your virtual environment ``virtualenv -p python3 venv3`` and activate
   it (``.\\venv3\\Scripts\\activate``)
#. Install dependencies: ``pip install .``
#. Run ``chickadee --help`` to get started.

Install the latest features without Git
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you would like to install the latest pre-release version, feel free to use
the above steps to clone the repository and install. You can also use pip
to directly install the latest master branch from GitHub by running:

```
pip install git+https://github.com/chapinb/chickadee.git
```

Contribution
------------

We appreciate contributions to the project! If you have an idea,
big or small, and want to lend a hand - feel free to follow the
steps in this guide to get started.

Looking for some inspiration? Check out the project `issues page
<https://github.com/chapinb/chickadee/issues>`_ for inspiration.
You are also welcome to contribute new ideas, features, or improvements.

We are happy to assist with any questions you have as you are working
on the project. Feel free to throw it as a new issue in GitHub. When
in doubt, just ask :) happy to provide guidance to those new to
contributing to projects!

The below steps outline the technical process for contributing to chickadee:

#. A `GitHub account <https://github.com/join>`_
#. Create a fork of the chickadee repository
#. Install git tools on your system
#. Clone your fork to your local system
#. Check out a new branch with a descriptive name.
   ie ``git checkout -b zipfile-support``
#. Install development dependencies in dev-requirements.txt
#. Make your modifications and write unit tests for new functionality
#. Submit a pull request to the main chickadee repository

A few tips to help get your new feature integrated smoothly:

* Ensure the whole project passes with ``flake8``. Avoid excluding linting
  warnings whenever possible.
* Run ``coverage run -m unittest discover`` and ensure all tests pass
  and all code files have at least 80% coverage. Avoid pragma statements
  whenever possible.
* Add documentation to your new functions/scripts and integrate into
  the overall project documentation. Build the documentation before
  submitting the pull request.
* As needed, update the argument and config file handling with help
  information to ensure users understand the purpose and functionality
  of the new capabilities.

When in doubt, reach out - we are happy to help with any of the above.

Usage & Examples
----------------

See :ref:`chickadee-usage` and :ref:`chickadee-examples`
for examples on using the ``chickadee`` command line tool.

Components
----------

Parsers
^^^^^^^

Collection of utilities for extracting IP addresses from different file
formats. The ``chickadee`` utility handles IP addresses provided via STDIN
and as argument parameters, though leverages these parsers to extract from
file content. The ``chickadee`` utility does iterate over directories to
expose files within folders recursively. With this, each parser needs to
accept a path to a file to read.

Resolvers
^^^^^^^^^

This is where the IP address is resolved by a third-party data source. Each
component is responsible for accepting one or more IP address and returning
resolution data. The third-party sources will not be distributed with this
library, each new resolver will have documentation to highlight the steps
required to prepare the data source for use by the resolver module.

The writers for libchickadee are also stored in this module.

Utilities
^^^^^^^^^

This includes the ``chickadee`` command line tool, used to interact with the
library from the command line.

"""

__author__ = 'Chapin Bryce'
__date__ = 20200805
__version__ = 20200805.0
__license__ = 'MIT Copyright 2020 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''
