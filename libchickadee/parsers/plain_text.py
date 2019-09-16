"""Parse IP addresses from plain text files
and feed to the Chickadee GeoIP API

Plain text files include logs, csvs, json, and other formats where ascii strings
contain IPv4 or IPv6 addresses.
"""

import binascii
import os
from gzip import GzipFile

from libchickadee.parsers import IPv4Pattern, IPv6Pattern, strip_ipv6

__author__ = 'Chapin Bryce'
__date__ = 20190907
__license__ = 'GPLv3 Copyright 2019 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''

class PlainTextParser(object):
    """Class to extract IP addresses from plain text
        and gzipped plain text files."""
    def __init__(self):
        self.ips = set()

    @staticmethod
    def is_gz_file(filepath):
        """Validate whether the input is GZipped."""
        with open(filepath, 'rb') as test_f:
            return binascii.hexlify(test_f.read(2)) == b'1f8b'

    def parse_file(self, file_entry):
        """Parse contents of the file."""
        if self.is_gz_file(file_entry):
            file_data = GzipFile(file_entry)
        else:
            file_data = open(file_entry, 'rb')

        for raw_line in file_data:
            line = raw_line.decode()
            for ipv4 in IPv4Pattern.findall(line):
                self.ips.add(ipv4)
            for ipv6 in IPv6Pattern.findall(line):
                self.ips.add(strip_ipv6(ipv6))

        if 'closed' in dir(file_data) and not file_data.closed:
            file_data.close()

if __name__ == "__main__":  # pragma: no cover
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help="File or folder to parse")
    args = parser.parse_args()

    ptparser = PlainTextParser()
    if os.path.isdir(args.path):
        for root, _, files in os.walk(args.path):
            for fentry in files:
                ptparser.parse_file(os.path.join(root, fentry))
    else:
        ptparser.parse_file(args.path)
    print("{} unique IPs discovered".format(len(ptparser.ips)))
