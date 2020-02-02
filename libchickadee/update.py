"""Script to check for available chickadee updates and alert the user."""

import requests
import sys

__author__ = 'Chapin Bryce'
__date__ = 20200202
__license__ = 'MIT Copyright 2020 Chapin Bryce'


def check_version(current_version):
    """Check version against pypi.org information"""

    url = 'https://pypi.org/pypi/chickadee/json'

    rdata = requests.get(url)

    version = rdata.json().get('info', {}).get('version', '0')

    if float(version) > current_version:
        msg = "Chickadee v.{} is available. Please update ".format(version) + \
            "using 'pip3 install --upgrade chickadee'."
        sys.stderr.write(msg+"\n")


if __name__ == "__main__":
    from libchickadee import __version__
    check_version(__version__)
