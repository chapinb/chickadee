"""Chickadee

An application to provide context for an IP address

"""

import argparse
import os
import sys
import logging
from pathlib import PurePath
from collections import Counter
import _io

# Third Party Libs
from tqdm import tqdm

# Import Backends
from libchickadee.backends.ipapi import Resolver, ProResolver

# Import Parsers
from libchickadee.parsers.plain_text import PlainTextParser
from libchickadee.parsers.xlsx import XLSXParser


__author__ = 'Chapin Bryce'
__date__ = 20200114
__license__ = 'GPLv3 Copyright 2019 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.

Will use the free rate limited ip-api.com service for resolution.
Please set an environment variable named CHICKADEE_API_KEY with the
value of your API key to enabled unlimited requests with the
commercial API
'''

logger = logging.getLogger(__name__)
_FIELDS = ','.join([  # Ordered list of fields to gather
    'query',
    'count', 'as', 'org', 'isp',
    'continent', 'country', 'regionName', 'city', 'district', 'zip',
    'mobile', 'proxy', 'hosting', 'reverse',
    'lat', 'lon', 'timezone',
    'status', 'message'
])


class Chickadee(object):
    """Class to handle chickadee script operations."""
    def __init__(self, outformat='json', outfile=sys.stdout, fields=_FIELDS):
        self.input_data = None
        self.outformat = outformat
        self.outfile = outfile
        self.fields = fields
        self.force_single = False
        self.lang = 'en'
        self.pbar = False
        self.resolve_ips = True

    def run(self, input_data):
        """Evaluate the input data format to extract and resolve IP addresses.

        Args:
            input_data (str or file_obj): User provided data containing IPs to
                resolve

        Returns:
            (list): List of dictionaries containing resolved hits
        """
        self.input_data = input_data
        results = []
        result_dict = {}
        # Extract and resolve IP addresses
        if not isinstance(self.input_data, _io.TextIOWrapper) and \
                os.path.isdir(self.input_data):
            logger.debug("Detected the data source as a directory")
            result_dict = self.dir_handler(self.input_data)  # Dir handler
        elif isinstance(self.input_data, _io.TextIOWrapper) or \
                os.path.isfile(self.input_data):
            logger.debug("Detected the data source as a file")
            result_dict = self.file_handler(self.input_data)  # File handler
        elif isinstance(self.input_data, str):
            logger.debug("Detected the data source as raw value(s)")
            result_dict = self.str_handler(self.input_data)  # String handler

        # Resolve if requested
        if self.resolve_ips:
            results = self.resolve(result_dict)
            return results

        return [{'query': k, 'count': v, 'message': 'No resolve'}
                for k, v in result_dict.items()]

    def write_output(self, results):
        """Write results to output format and/or files

        Args:
            results (list): List of GeoIP results
        """

        if self.outformat == 'csv':
            logger.debug("Writing CSV report")
            Resolver.write_csv(self.outfile, results, self.fields)
        elif self.outformat == 'json':
            logger.debug("Writing json report")
            Resolver.write_json(self.outfile, results, self.fields)
        elif self.outformat == 'jsonl':
            logger.debug("Writing json lines report")
            Resolver.write_json(self.outfile, results, self.fields, lines=True)

    @staticmethod
    def get_api_key():
        """Retrieve an API key set as an envar."""
        api_key = os.environ.get('CHICKADEE_API_KEY', None)
        if api_key is not None and len(api_key):
            return api_key
        return None

    @staticmethod
    def str_handler(data):
        """Handle string input of one or more IP addresses and executes the query

        Args:
            input_data (str): raw input data from user
            fields (list): List of fields to query for

        Return:
            data_dict (dict): dictionary of distinct IP addresses to resolve.
        """
        if isinstance(data, str) and ',' in data:
            # List of IPs
            raw_data = data.strip().split(',')
        elif isinstance(data, str):
            # Single IP
            raw_data = [data.strip()]
        else:
            raise TypeError('Unsupported input provided.')

        # Generate a distinct list with count
        data_dict = {}
        for x in raw_data:
            if x not in data_dict:
                data_dict[x] = 0
            data_dict[x] += 1
        return data_dict

    def resolve(self, data_dict):
        """Resolve IP addresses stored as keys within `data_dict`. The values
        for each key should represent the number of occurances of an IP within
        a data set.

        Args:
            data_dict (dict): Structured as {'IP': COUNT}

        Returns:
            all_results (list): resolved GeoIP data
        """
        distinct_ips = list(data_dict.keys())

        logger.info("Identified {} distinct IPs for resolution".format(
            len(distinct_ips)))

        api_key = self.get_api_key()

        if api_key:
            resolver = ProResolver(api_key, fields=self.fields, lang=self.lang)
        else:
            resolver = Resolver(fields=self.fields, lang=self.lang)

        if self.pbar:
            resolver.pbar = self.pbar

        logger.info("Resolving IPs")
        if self.force_single:
            results = []
            data = distinct_ips
            if self.pbar:
                data = tqdm(distinct_ips, desc="Resolving IPs",
                            unit_scale=True)

            for element in data:
                resolver.data = element
                results.append(resolver.single())
        else:
            results = resolver.query(distinct_ips)

        logger.info("Resolved IPs")

        # Add frequency information to results
        if 'count' in self.fields:
            updated_results = []
            for result in results:
                query = str(result.get('query', ''))
                result['count'] = int(data_dict.get(query, '0'))
                updated_results.append(result)

            return updated_results
        return results

    @staticmethod
    def file_handler(file_path):
        """Handle parsing IP addresses from a file

        Args:
            input_data (str): raw input data from use
            fields (list): List of fields to query for

        Return:
            (list): all query results from extracted IPs
        """
        if isinstance(file_path, _io.TextIOWrapper):
            is_stream = True
            # Extract IPs with proper handler
            logger.debug("Extracting IPs from STDIN")
        else:
            is_stream = False
            # Extract IPs with proper handler
            logger.debug("Extracting IPs from {}".format(file_path))

        if not is_stream and file_path.endswith('xlsx'):
            file_parser = XLSXParser()
        else:
            file_parser = PlainTextParser()
        try:
            file_parser.parse_file(file_path, is_stream)
        except Exception:
            logger.warning("Failed to parse {}".format(file_path))
        return file_parser.ips

    def dir_handler(self, file_path):
        """Handle parsing IP addresses from files recursively

        Args:
            input_data (str): raw input data from use
            fields (list): List of fields to query for

        Return:
            (list): all query results from extracted IPs
        """
        result_dict = {}
        for root, _, files in os.walk(file_path):
            for fentry in files:
                file_entry = os.path.join(root, fentry)
                logger.debug("Parsing file {}".format(file_entry))
                file_results = self.file_handler(file_entry)
                logger.debug("Parsed file {}, {} results".format(
                    file_entry, len(file_results)))
                result_dict = dict(Counter(result_dict)+Counter(file_results))
        logger.debug("{} total distinct IPs discovered".format(
            len(result_dict)))
        return result_dict


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
        '%(funcName)s:%(lineno)d - %(message)s')

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


class CustomArgFormatter(argparse.RawTextHelpFormatter,
                         argparse.ArgumentDefaultsHelpFormatter):
    """Custom argparse formatter class"""


def arg_handling():
    """Argument handling."""
    parser = argparse.ArgumentParser(
        description=__desc__,
        formatter_class=CustomArgFormatter,
        epilog="Built by {}, v.{}".format(__author__, __date__)
    )
    parser.add_argument(
        'data',
        help="Either an IP address, comma delimited list of IP addresses, "
             "or path to a file or folder containing files to check for "
             "IP address values. Currently supported file types: "
             "plain text (ie logs, csv, json), gzipped plain text, xlsx "
             "(must be xlsx extension). Can accept plain text data as stdin.",
        nargs='*',
        default=sys.stdin
    )
    parser.add_argument('-f', '--fields',
                        help='Comma separated fields to query',
                        default=_FIELDS)
    parser.add_argument('-t', '--output-format',
                        help='Output format',
                        choices=['json', 'jsonl', 'csv'],
                        default='jsonl')
    parser.add_argument('-w', '--output-file',
                        help='Path to file to write output',
                        default=sys.stdout, metavar='FILENAME.JSON')
    parser.add_argument('-n', '--no-resolve', action='store_false',
                        help="Only extract IP addresses, don't resolve.")
    parser.add_argument('-s', '--single',
                        help="Use the significantly slower single item API. "
                             "Adds reverse DNS.",
                        action='store_true')
    parser.add_argument('--lang', help="Language", default='en',
                        choices=['en', 'de', 'es', 'pt-BR', 'fr', 'ja',
                                 'zh-CN', 'ru'])
    parser.add_argument('-p', '--progress', help="Enable progress bar",
                        action="store_true")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Include debug log messages')
    parser.add_argument('-V', '--version', action='version',
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
    logger.info("Configuring Chickadee")
    chickadee = Chickadee(fields=fields)
    chickadee.resolve_ips = args.no_resolve
    chickadee.force_single = args.single
    chickadee.lang = args.lang
    chickadee.pbar = args.progress

    logger.info("Parsing input")
    if isinstance(args.data, list):
        data = []
        for x in args.data:
            res = chickadee.run(x)
            data += res
    else:
        data = chickadee.run(args.data)

    logger.info("Writing output")
    chickadee.outfile = args.output_file
    chickadee.outformat = args.output_format
    chickadee.write_output(data)

    logger.info("Chickadee complete")


if __name__ == "__main__":
    entry()
