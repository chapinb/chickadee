"""Parse IP addresses from XLSX files
and feed to the Chickadee GeoIP API
"""

import os

from openpyxl import load_workbook

from libchickadee.parsers import IPv4Pattern, IPv6Pattern, strip_ipv6


__author__ = 'Chapin Bryce'
__date__ = 20200107
__license__ = 'GPLv3 Copyright 2019 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''


class XLSXParser(object):
    """Class to extract IP addresses from xlsx workbooks."""
    def __init__(self):
        self.ips = dict()

    def parse_file(self, file_entry, is_stream=False):
        """Parse xlsx contents"""
        wb = load_workbook(file_entry)

        for sheet in wb.sheetnames:
            ws = wb[sheet]
            for row in ws.iter_rows():
                for cell in row:
                    if isinstance(cell.value, (str, bytes)):
                        self.check_ips(cell.value)

    def check_ips(self, data):
        """Check data for IP addresses."""
        for ipv4 in IPv4Pattern.findall(data):
            if ipv4 not in self.ips:
                self.ips[ipv4] = 0
            self.ips[ipv4] += 1
        for ipv6 in IPv6Pattern.findall(data):
            if strip_ipv6(ipv6) not in self.ips:
                self.ips[strip_ipv6(ipv6)] = 0
            self.ips[strip_ipv6(ipv6)] += 1


if __name__ == '__main__':  # pragma: no cover
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help="File or folder to parse")
    args = parser.parse_args()

    xlparser = XLSXParser()
    if os.path.isdir(args.path):
        for root, _, files in os.walk(args.path):
            for fentry in files:
                xlparser.parse_file(os.path.join(root, fentry))
    else:
        xlparser.parse_file(args.path)
    print("{} unique IPs discovered".format(len(xlparser.ips)))
