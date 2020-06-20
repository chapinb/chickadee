"""Script to check for available chickadee updates and alert the user."""

import requests
import sys

__author__ = 'Chapin Bryce'
__date__ = 20200202
__license__ = 'MIT Copyright 2020 Chapin Bryce'


def get_pypi_version():
    """Check pypi.org for version information"""
    url = 'https://pypi.org/pypi/chickadee/json'
    rdata = requests.get(url)
    return float(rdata.json().get('info', {}).get('version', '0'))


def update_available(current_version):
    """Check version against pypi.org information"""
    pypi_version = get_pypi_version()
    return pypi_version > current_version


if __name__ == "__main__":
    from libchickadee import __version__
    if update_available(__version__):
        sys.stderr.write(
            "Chickadee update is available. Please update "
            "using 'pip3 install --upgrade chickadee'.\n"
        )
