"""Parse IP addresses from plain text files
and feed to the Chickadee GeoIP API

Plain text files include logs, csvs, json, and other formats where ascii
strings contain IPv4 or IPv6 addresses.
"""

import binascii
import os
from gzip import GzipFile

from libchickadee.parsers import IPv4Pattern, IPv6Pattern, strip_ipv6

__author__ = 'Chapin Bryce'
__date__ = 20200114
__license__ = 'GPLv3 Copyright 2019 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''


class PlainTextParser(object):
    """Class to extract IP addresses from plain text
        and gzipped plain text files."""
    def __init__(self):
        self.ips = dict()

    @staticmethod
    def is_gz_file(filepath):
        """Validate whether the input is GZipped."""
        with open(filepath, 'rb') as test_f:
            return binascii.hexlify(test_f.read(2)) == b'1f8b'

    def parse_file(self, file_entry, is_stream=False):
        """Parse contents of the file."""
        if not is_stream:
            if self.is_gz_file(file_entry):
                file_data = GzipFile(filename=file_entry)
            else:
                file_data = open(file_entry, 'rb')
        else:
            if binascii.hexlify(file_entry.buffer.read(2)) == b'1f8b':
                file_data = GzipFile(fileobj=file_entry)
            else:
                file_data = file_entry.buffer

        for raw_line in file_data:
            line = raw_line.decode()
            for ipv4 in IPv4Pattern.findall(line):
                if ipv4 not in self.ips:
                    self.ips[ipv4] = 0
                self.ips[ipv4] += 1
            for ipv6 in IPv6Pattern.findall(line):
                if strip_ipv6(ipv6) not in self.ips:
                    self.ips[strip_ipv6(ipv6)] = 0
                self.ips[strip_ipv6(ipv6)] += 1

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
