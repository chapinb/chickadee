"""
Plain Text Parser
==================

Parse IP addresses from plain text files. Plain text files include logs,
CSVs, JSON, and other formats where ascii strings contain IPv4 or IPv6
addresses.

Also supported reading from gzipped compressed plain text data without needing
to first decompress it.

"""

import binascii
import os
from gzip import GzipFile

from libchickadee.parsers import ParserBase

__author__ = 'Chapin Bryce'
__date__ = 20200114
__license__ = 'MIT Copyright 2020 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''


class PlainTextParser(ParserBase):
    """Class to extract IP addresses from plain text
        and gzipped plain text files."""
    def __init__(self):
        super()
        self.ips = dict()

    @staticmethod
    def is_gz_file(filepath):
        """Validate whether the input is GZipped.

        Args:
            filepath (str): File path to test.

        Returns:
            (bool): True if a gzip file signature is identified.
        """
        with open(filepath, 'rb') as test_f:
            return binascii.hexlify(test_f.read(2)) == b'1f8b'

    def parse_file(self, file_entry, is_stream=False):
        """Parse contents of the file and extract IP addresses.

        Will read from STDIN or path to a file. Stores results in ``self.ips``.

        Args:
            file_entry (str or file_obj): Path to file for reading.
            is_stream (bool): Whether the input file is a file to open or a
                file-like object.

        Returns:
            None
        """
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
            self.check_ips(line)

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
