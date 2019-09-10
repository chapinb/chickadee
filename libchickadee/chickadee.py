"""Chickadee

An application to provide context for an IP address

"""

import argparse
import os
import sys

from libchickadee.backends.ipapi import Resolver
from libchickadee.parsers.plain_text import PlainTextParser

__author__ = 'Chapin Bryce'
__date__ = 20190910
__license__ = 'GPLv3 Copyright 2019 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''

FIELDS = ','.join([ # Ordered list of fields to gather
    'query',
    'as', 'org', 'isp',
    'continent', 'country', 'regionName', 'city', 'district', 'zip',
    'mobile', 'proxy', 'reverse',
    'lat', 'lon', 'timezone',
    'status', 'message'
])

def str_handler(input_data, fields=None):
    """Handle string input of one or more IP addresses and executes the query

    Args:
        input_data (str): raw input data from use
        fields (list): List of fields to query for

    Return:
        all_results (list): list of distinct IP addresses to resolve.
    """
    if isinstance(input_data, str) and ',' in input_data:
        input_data = input_data.split(',')

    resolver = Resolver()
    if fields:
        resolver.fields = fields
    if len(input_data) > resolver.bulk_limit * resolver.ratelimit:
        sys.stderr.write(
              "[!] Warning: due to rate limiting, this resolution will take "
              "at least {} minutes. Consider purchasing an API key for "
              "increased query performance\n".format(
                  len(input_data)/resolver.bulk_limit/resolver.ratelimit))
    results = resolver.query(input_data)
    all_results = [x for x in results]
    return all_results

def file_handler(input_data, fields):
    """Handle parsing IP addresses from a file

    Args:
        input_data (str): raw input data from use
        fields (list): List of fields to query for

    Return:
        (list): all query results from extracted IPs
    """
    sys.stderr.write("Extracting IPs from files\n")
    ptparser = PlainTextParser()
    ptparser.parse_file(input_data)
    sys.stderr.write(
        "{} IPs discovered, resolving...\n".format(len(ptparser.ips)))
    return str_handler(list(ptparser.ips), fields)


def dir_handler(input_data, fields):
    """Handle parsing IP addresses from files recursively

    Args:
        input_data (str): raw input data from use
        fields (list): List of fields to query for

    Return:
        (list): all query results from extracted IPs
    """
    ptparser = PlainTextParser()
    for root, _, files in os.walk(input_data):
        for fentry in files:
            ptparser.parse_file(os.path.join(root, fentry))
    return str_handler(list(ptparser.ips), fields)


def main(input_data, outformat='json', outfile=None, fields=FIELDS):
    """Evaluate the input data format to extract and resolve IP addresses.

    Args:
        input_data (str or file_obj): User provided data containing IPs to
            resolve
    """

    # Extract and resolve IP addresses
    if os.path.isdir(input_data):
        results = dir_handler(input_data, fields) # Directory handler
    elif os.path.isfile(input_data):
        results = file_handler(input_data, fields) # File handler
    elif isinstance(input_data, str):
        results = str_handler(input_data, fields) # String handler

    # Write results to output format and/or files
    if outformat == 'csv':
        Resolver.write_csv(outfile, results, fields)
    elif outformat == 'json':
        Resolver.write_json(outfile, results)
    elif outformat == 'jsonl':
        Resolver.write_json(outfile, results, lines=True)

def arg_handling():
    """Argument handling."""
    parser = argparse.ArgumentParser(
        description='Sample Argparse',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Built by {}, v.{}".format(__author__, __date__)
    )
    parser.add_argument(
        'data',
        help="Either an IP address, comma delimited list of IP addresses, "
             "or path to a file or folder containing files to check for "
             "IP address values. Currently supported file types: "
             "plain text (ie logs, csv, json), gzipped plain text"
    )
    parser.add_argument('-f', help='Comma separated fields to query',
                        default=FIELDS)
    parser.add_argument('-t', help='Output format',
                        choices=['json', 'jsonl', 'csv'],
                        default='jsonl')
    parser.add_argument('-w', help='Path to file to write output',
                        default=sys.stdout, metavar='FILENAME.JSON')
    args = parser.parse_args()
    return args

def entry(args=None):
    """Entrypoint for package script"""
    args = arg_handling()
    fields = args.f.split(',')
    main(args.data, outformat=args.t, outfile=args.w, fields=fields)


if __name__ == "__main__":
    entry()
