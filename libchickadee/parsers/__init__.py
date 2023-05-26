"""
Common Parser Utilities
=======================

Collection of input parser utilities to extract IP addresses.

This includes common regex patterns and utilities for extracting IP addresses
for resolution.

"""

import json
import os
import re
import sys

from netaddr import IPAddress

__author__ = 'Chapin Bryce'
__date__ = 20200107
__license__ = 'MIT Copyright 2020 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''

# FROM https://gist.github.com/dfee/6ed3a4b05cfe7a6faf40a2102408d5d8
IPV4SEG = r'(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])'
IPV4ADDR = f'(?:(?:{IPV4SEG}' + r'\.){3,3}' + IPV4SEG + r')'

IPV6SEG = r'(?:(?:[0-9a-fA-F]){1,4})'
IPV6GROUPS = (
    f'(?:{IPV6SEG}' + r':){7,7}' + IPV6SEG,
    f'(?:{IPV6SEG}' + r':){1,7}:',
    f'(?:{IPV6SEG}' + r':){1,6}:' + IPV6SEG,
    f'(?:{IPV6SEG}' + r':){1,5}(?::' + IPV6SEG + r'){1,2}',
    f'(?:{IPV6SEG}' + r':){1,4}(?::' + IPV6SEG + r'){1,3}',
    f'(?:{IPV6SEG}' + r':){1,3}(?::' + IPV6SEG + r'){1,4}',
    f'(?:{IPV6SEG}' + r':){1,2}(?::' + IPV6SEG + r'){1,5}',
    f'{IPV6SEG}:(?:(?::{IPV6SEG}' + r'){1,6})',
    f':(?:(?::{IPV6SEG}' + r'){1,7}|:)',
    f'fe80:(?::{IPV6SEG}' + r'){0,4}%[0-9a-zA-Z]{1,}',
    r'::(?:ffff(?::0{1,4}){0,1}:){0,1}[^\s:]' + IPV4ADDR,
    f'(?:{IPV6SEG}' + r':){1,4}:[^\s:]' + IPV4ADDR,
)

# Reverse rows for greedy match
IPV6ADDR = '|'.join(f'(?:{g})' for g in IPV6GROUPS[::-1])

IPv4Pattern = re.compile(IPV4ADDR)
IPv6Pattern = re.compile(IPV6ADDR)


def run_parser_from_cli(args, parser_obj):  # pragma: no cover
    """Allow a parser to run from the command line, both for testing and increased usability."""
    if os.path.isdir(args.path):
        for root, _, files in os.walk(args.path):
            for fentry in files:
                parser_obj.parse_file(os.path.join(root, fentry))
    else:
        parser_obj.parse_file(args.path)
    sys.stderr.write(f"{len(parser_obj.ips)} unique IPs discovered, shown below with their frequency.\n")
    for ip, count in parser_obj.ips.items():
        print(json.dumps({"count": count, "ip": ip}))


class ParserBase:
    """Base class for parsers, containing common utilities."""
    def __init__(self, ignore_bogon=True):
        """Configure the parser and set default values."""
        self.ignore_bogon = ignore_bogon
        self.ips = {}

    def check_ips(self, data):
        """Check data for IP addresses. Results stored in ``self.ips``.

        Args:
            data (str): String to search for IP address content.

        Returns:
            None
        """
        for ipv4 in IPv4Pattern.findall(data):
            if self.ignore_bogon and self.is_bogon(ipv4):
                continue
            if ipv4 not in self.ips:
                self.ips[ipv4] = 0
            self.ips[ipv4] += 1
        for ipv6 in IPv6Pattern.findall(data):
            ipv6 = self.strip_ipv6(ipv6)
            if self.ignore_bogon and self.is_bogon(ipv6):
                continue
            if ipv6 not in self.ips:
                self.ips[ipv6] = 0
            self.ips[ipv6] += 1

    @staticmethod
    def strip_ipv6(ipv6_addr):
        """Isolate IPv6 Value containing a ``%`` symbol.

        Args:
            ipv6_addr (str): Raw IPv6 IP address to strip.

        Returns:
            (str): IP address base.
        """
        if '%' in ipv6_addr:
            ip, _ = ipv6_addr.split('%')
        else:
            ip = ipv6_addr
        return ip

    @staticmethod
    def is_bogon(ip_addr):
        """Identifies whether an IP address is a known BOGON.

        Args:
            ip_addr (str): Valid IP address to check.

        Returns:
            (bool): Whether or not the IP is a known BOGON address.
        """
        ip = IPAddress(ip_addr)
        return bool((ip.is_private() or ip.is_link_local() or
                     ip.is_reserved() or ip.is_multicast()))
