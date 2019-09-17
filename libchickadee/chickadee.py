"""Chickadee

An application to provide context for an IP address

"""

import argparse
import os
import sys
import logging
from pathlib import PurePath

# Import Backends
from libchickadee.backends.ipapi import Resolver

# Import Parsers
from libchickadee.parsers.plain_text import PlainTextParser
from libchickadee.parsers.xlsx import XLSXParser


__author__ = 'Chapin Bryce'
__date__ = 20190917
__license__ = 'GPLv3 Copyright 2019 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''

logger = logging.getLogger(__name__)
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
        logger.warning(
            "[!] Warning: due to rate limiting, this resolution will take "
            "at least {} minutes. Consider purchasing an API key for "
            "increased query performance".format(
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
    # Extract IPs with proper handler
    logger.debug("Extracting IPs from {}".format(input_data))
    if input_data.endswith('xlsx'):
        file_parser = XLSXParser()
    else:
        file_parser = PlainTextParser()
    try:
        file_parser.parse_file(input_data)
    except Exception:
        logger.warn("Failed to parse {}".format(input_data))
    return file_parser.ips


def dir_handler(input_data, fields):
    """Handle parsing IP addresses from files recursively

    Args:
        input_data (str): raw input data from use
        fields (list): List of fields to query for

    Return:
        (list): all query results from extracted IPs
    """
    result_set = set()
    for root, _, files in os.walk(input_data):
        for fentry in files:
            file_results = file_handler(os.path.join(root, fentry),
                                        fields)
            result_set = result_set | file_results
            logger.debug("{} total distinct IPs discovered".format(
                len(result_set)))
    return str_handler(list(result_set), fields)


def main(input_data, outformat='json', outfile=None, fields=FIELDS):
    """Evaluate the input data format to extract and resolve IP addresses.

    Args:
        input_data (str or file_obj): User provided data containing IPs to
            resolve
    """

    # Extract and resolve IP addresses
    if os.path.isdir(input_data):
        logger.debug("Detected the data source as a directory")
        results = dir_handler(input_data, fields) # Directory handler
    elif os.path.isfile(input_data):
        logger.debug("Detected the data source as a file")
        result_set = file_handler(input_data, fields) # File handler
        results = str_handler(list(result_set), fields)
    elif isinstance(input_data, str):
        logger.debug("Detected the data source as raw value(s)")
        results = str_handler(input_data, fields) # String handler

    # Write results to output format and/or files
    if outformat == 'csv':
        logger.debug("Writing CSV report")
        Resolver.write_csv(outfile, results, fields)
    elif outformat == 'json':
        logger.debug("Writing json report")
        Resolver.write_json(outfile, results)
    elif outformat == 'jsonl':
        logger.debug("Writing json lines report")
        Resolver.write_json(outfile, results, lines=True)


def setup_logging(path, verbose=False):
    """Function to setup logging configuration and test it."""
    # Allow us to modify the `logger` variable within a function
    global logger

    # Set logger object, uses module's name
    logger = logging.getLogger(name=__name__)

    # Set default logger level to DEBUG. You can change this later
    logger.setLevel(logging.DEBUG)

    # Logging formatter. Best to keep consistent for most usecases
    log_format = logging.Formatter(
        '%(asctime)s %(filename)s %(levelname)s %(module)s '
        '%(funcName)s %(lineno)d %(message)s')

    # Setup STDERR logging, allowing you uninterrupted
    # STDOUT redirection
    stderr_handle = logging.StreamHandler(stream=sys.stderr)
    if verbose:
        stderr_handle.setLevel(logging.DEBUG)
    else:
        stderr_handle.setLevel(logging.INFO)
    stderr_handle.setFormatter(log_format)

    # Setup file logging
    file_handle = logging.FileHandler(path, 'a')
    file_handle.setLevel(logging.DEBUG)
    file_handle.setFormatter(log_format)

    # Add handles
    logger.addHandler(stderr_handle)
    logger.addHandler(file_handle)


def arg_handling():
    """Argument handling."""
    parser = argparse.ArgumentParser(
        description=__desc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Built by {}, v.{}".format(__author__, __date__)
    )
    parser.add_argument(
        'data',
        help="Either an IP address, comma delimited list of IP addresses, "
             "or path to a file or folder containing files to check for "
             "IP address values. Currently supported file types: "
             "plain text (ie logs, csv, json), gzipped plain text, xlsx "
             "(must be xlsx extension)."
    )
    parser.add_argument('-f', '--fields',
                        help='Comma separated fields to query',
                        default=FIELDS)
    parser.add_argument('-t', '--output-format',
                        help='Output format',
                        choices=['json', 'jsonl', 'csv'],
                        default='jsonl')
    parser.add_argument('-w', '--output-file',
                        help='Path to file to write output',
                        default=sys.stdout, metavar='FILENAME.JSON')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Include debug log messages')
    parser.add_argument('--version', action='version',
                        help='Displays version',
                        version=str(__date__))
    parser.add_argument(
        '-l',
        '--log',
        help="Path to log file",
        default=os.path.abspath(os.path.join(
            os.getcwd(), PurePath(__file__).name.rsplit('.', 1)[0] + '.log'))
    )
    args = parser.parse_args()
    return args


def entry(args=None):
    """Entrypoint for package script"""
    args = arg_handling()
    fields = args.fields.split(',')
    setup_logging(args.log, args.verbose)
    logger.info("Starting Chickadee")
    for arg in vars(args):
        logger.debug("Argument {} is set to {}".format(
            arg, getattr(args, arg)
        ))
    main(args.data, outformat=args.output_format,
         outfile=args.output_file, fields=fields)
    logger.info("Chickadee complete")

if __name__ == "__main__":
    entry()
