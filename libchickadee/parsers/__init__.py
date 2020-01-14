"""Collection of input parsers to extract IP addresses."""

import re

__author__ = 'Chapin Bryce'
__date__ = 20200107
__license__ = 'GPLv3 Copyright 2019 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''

# FROM https://gist.github.com/dfee/6ed3a4b05cfe7a6faf40a2102408d5d8
IPV4SEG = r'(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])'
IPV4ADDR = r'(?:(?:' + IPV4SEG + r'\.){3,3}' + IPV4SEG + r')'

IPV6SEG = r'(?:(?:[0-9a-fA-F]){1,4})'
IPV6GROUPS = (
    # 1:2:3:4:5:6:7:8
    r'(?:' + IPV6SEG + r':){7,7}' + IPV6SEG,
    # 1:: | 1:2:3:4:5:6:7::
    r'(?:' + IPV6SEG + r':){1,7}:',
    # 1::8 | 1:2:3:4:5:6::8 | 1:2:3:4:5:6::8
    r'(?:' + IPV6SEG + r':){1,6}:' + IPV6SEG,
    # 1::7:8 | 1:2:3:4:5::7:8 | 1:2:3:4:5::8
    r'(?:' + IPV6SEG + r':){1,5}(?::' + IPV6SEG + r'){1,2}',
    # 1::6:7:8 | 1:2:3:4::6:7:8 | 1:2:3:4::8
    r'(?:' + IPV6SEG + r':){1,4}(?::' + IPV6SEG + r'){1,3}',
    # 1::5:6:7:8 | 1:2:3::5:6:7:8 | 1:2:3::8
    r'(?:' + IPV6SEG + r':){1,3}(?::' + IPV6SEG + r'){1,4}',
    # 1::4:5:6:7:8 | 1:2::4:5:6:7:8 | 1:2::8
    r'(?:' + IPV6SEG + r':){1,2}(?::' + IPV6SEG + r'){1,5}',
    # 1::3:4:5:6:7:8 | 1::3:4:5:6:7:8 | 1::8
    IPV6SEG + r':(?:(?::' + IPV6SEG + r'){1,6})',
    # ::2:3:4:5:6:7:8 | ::2:3:4:5:6:7:8 | ::8 | ::
    r':(?:(?::' + IPV6SEG + r'){1,7}|:)',
    # fe80::7:8%eth0 | fe80::7:8%1
    # (link-local IPv6 addresses with zone index)
    r'fe80:(?::' + IPV6SEG + r'){0,4}%[0-9a-zA-Z]{1,}',
    # ::255.255.255.255 | ::ffff:255.255.255.255 | ::ffff:0:255.255.255.255
    # (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
    r'::(?:ffff(?::0{1,4}){0,1}:){0,1}[^\s:]' + IPV4ADDR,
    # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33
    # (IPv4-Embedded IPv6 Address)
    r'(?:' + IPV6SEG + r':){1,4}:[^\s:]' + IPV4ADDR,
)

# Reverse rows for greedy match
IPV6ADDR = '|'.join(['(?:{})'.format(g) for g in IPV6GROUPS[::-1]])

IPv4Pattern = re.compile(IPV4ADDR)
IPv6Pattern = re.compile(IPV6ADDR)


def strip_ipv6(ipv6_addr):
    """Isolate IPv6 Value"""
    if '%' in ipv6_addr:
        ip, _ = ipv6_addr.split('%')
    else:
        ip = ipv6_addr
    return ip
