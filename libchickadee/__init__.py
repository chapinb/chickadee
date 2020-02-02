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

Backends
^^^^^^^^

This is where the IP address is resolved by a third-party data source. Each
component is responsible for accepting one or more IP address and returning
resolution data. The third-party sources will not be distributed with this
library, each new backend will have documentation to highlight the steps
required to prepare the data source for use by the backend module.

The writers for libchickadee are also stored in this module.

Utilities
^^^^^^^^^

This includes the ``chickadee`` command line tool, used to interact with the
library from the command line.

"""

__author__ = 'Chapin Bryce'
__date__ = 20200107
__version__ = 20200202
__license__ = 'MIT Copyright 2020 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''
