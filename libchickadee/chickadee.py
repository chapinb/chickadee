"""
chickadee.py
============

A command-line application to provide context for an IP address.

This utility leveraged libchickadee to extract, resolve, and report IP
addresses. Please see :ref:`installation` instructions for details
on setting up this tool on your system.

.. _chickadee-usage:

Usage
-----

.. code-block:: text

    usage: chickadee [-h] [-f FIELDS] [-t {json,jsonl,csv}] [-w FILENAME.JSON]
                    [-n] [-s] [--lang {en,de,es,pt-BR,fr,ja,zh-CN,ru}]
                    [-c CONFIG] [-p] [-v] [-V] [-l LOG]
                    [data [data ...]]

    Yet another GeoIP resolution tool.

    Will use the free rate limited ip-api.com service for resolution.
    Please set an environment variable named CHICKADEE_API_KEY with the
    value of your API key to enabled unlimited requests with the
    commercial API

    positional arguments:
    data         Either an IP address, comma delimited list of IP addresses, or
                 path to a file or folder containing files to check for IP
                 address values. Currently supported file types: plain text
                 (ie logs, csv, json), gzipped plain text, xlsx (must be xlsx
                 extension). Can accept plain text data as stdin.
                 (default: <_io.TextIOWrapper name='<stdin>' mode='r'
                            encoding='UTF-8'>)

    optional arguments:
    -h, --help            show this help message and exit
    -f FIELDS, --fields FIELDS
                            Comma separated fields to query
                            (default: query,count,as,org,isp,continent,country,
                                      regionName,city,district,zip,mobile,
                                      proxy,hosting,reverse,lat,lon,timezone,
                                      status,message)
    -t {json,jsonl,csv}, --output-format {json,jsonl,csv}
                            Output format (default: jsonl)
    -w FILENAME.JSON, --output-file FILENAME.JSON
                            Path to file to write output
                            (default: <_io.TextIOWrapper name='<stdout>'
                                       mode='w' encoding='UTF-8'>)
    -n, --no-resolve      Only extract IP addresses, don't resolve.
                          (default: False)
    -s, --single          Use the significantly slower single item API.
                          Adds reverse DNS. (default: False)
    --lang {en,de,es,pt-BR,fr,ja,zh-CN,ru}
                            Language (default: en)
    -c CONFIG, --config CONFIG
                            Path to config file to load (default: None)
    -p, --progress        Enable progress bar (default: False)
    -v, --verbose         Include debug log messages (default: False)
    -V, --version         Displays version
    -l LOG, --log LOG     Path to log file (default: ./chickadee.log)

    Built by Chapin Bryce, v.20200202

.. _chickadee-examples:

chickadee Examples
----------------------

Input options
^^^^^^^^^^^^^

Parsing a single IP address:

``chickadee 1.1.1.1``

Parsing multiple IP addresses:

``chickadee 1.1.1.1,2.2.2.2``

Parsing IPs from STDIN:

``cat file.txt | chickadee``

Parsing IPs from a file:

``chickadee file.txt``

Parsing IPs from a folder, recursively:

``chickadee folder/``

Output options
^^^^^^^^^^^^^^

Reporting to JSON format:

``chickadee 1.1.1.1 -t json``

Reporting to JSON lines format:

``chickadee 1.1.1.1 -t jsonl``

Reporting to CSV format:

``chickadee 1.1.1.1 -t csv``

Other Arguments
^^^^^^^^^^^^^^^

Changing the fields to resolve and report on:

``chickadee -f query,count,asn,isp,org 1.1.1.1``

Changing the output location (STDOUT by default)

``chickadee 1.1.1.1 -w resolve.json``

Only extract IP addresses, don't resolve:

``chickadee -n 1.1.1.1``

Module Documentation
--------------------

"""

import argparse
import os
import sys
import logging
from pathlib import PurePath
from collections import Counter
import _io
import configparser

# Third Party Libs
from tqdm import tqdm

# Import lib features
from libchickadee import __version__
from libchickadee.update import update_available

# Import Backends
from libchickadee.backends.ipapi import Resolver, ProResolver

# Import Parsers
from libchickadee.parsers.plain_text import PlainTextParser
from libchickadee.parsers.xlsx import XLSXParser


__author__ = 'Chapin Bryce'
__date__ = 20200407.2
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
    """Class to handle chickadee script operations.

    Args:
        outformat (str): One of ``json``, ``jsonl``, ``csv``
        outfile (str or file_obj): Destination to write report.
        fields (list): Collection of fields to resolve and report on.

    Returns:
        None

    Examples:
        >>> chickadee = Chickadee()
        >>> resolution = chickadee.run('1.1.1.1')
        >>> print(resolution)

    """
    def __init__(self, outformat='json', outfile=sys.stdout, fields=_FIELDS):
        self.input_data = None
        self.outformat = outformat
        self.outfile = outfile
        self.fields = fields
        self.force_single = False
        self.ignore_bogon = True
        self.lang = 'en'
        self.pbar = False
        self.resolve_ips = True

    def run(self, input_data, api_key=None):
        """Evaluate the input data format to extract and resolve IP addresses.

        Will check the ``self.input_data`` type and select the proper handler.
        This includes handling files, directories, STDIN, and python strings
        and sending to the proper handler to extract IPs

        Once extracted, the IP addresses are passed to the ``self.resolve()``
        method if the ``self.resolve_ips`` option is enabled.

        Args:
            input_data (str or file_obj): User provided data containing IPs to
                resolve
            api_key (str): API Key for backend GeoIP resolver.

        Returns:
            (list): List of dictionaries containing resolved hits.
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
            # File handler
            result_dict = self.file_handler(self.input_data, self.ignore_bogon)

        elif isinstance(self.input_data, str):
            logger.debug("Detected the data source as raw value(s)")
            result_dict = self.str_handler(self.input_data)  # String handler

        logger.info("Extracted {} distinct IPs".format(
            len(list(result_dict.keys()))))

        # Resolve if requested
        if self.resolve_ips:
            results = self.resolve(result_dict, api_key)
            return results

        return [{'query': k, 'count': v, 'message': 'No resolve'}
                for k, v in result_dict.items()]

    @staticmethod
    def get_api_key():
        """Retrieve an API key set as an envar. Looks for value in
        ``CHICKADEE_API_KEY``. May be depreciated in the near future.

        Returns:
            (str): API key, if found
        """
        api_key = os.environ.get('CHICKADEE_API_KEY', None)
        if api_key is not None and len(api_key):
            return api_key
        return None

    @staticmethod
    def str_handler(data):
        """Handle string input of one or more IP addresses and returns the
        distinct IPs with their associated frequency count.

        Args:
            data (str): raw input data from user

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

    @staticmethod
    def file_handler(file_path, ignore_bogon):
        """Handle parsing IP addresses from a file.

        Will evaluate format of input file or file stream. Currently supports
        plain text, gzipped compressed plain text, and xlsx.

        Args:
            file_path (str or file_obj): Path of file to read or stream.
            ignore_bogon (bool): Whether to include BOGON addresses in results.

        Return:
            data_dict (dict): dictionary of distinct IP addresses to resolve.
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
            file_parser = XLSXParser(ignore_bogon)
        else:
            file_parser = PlainTextParser(ignore_bogon)
        try:
            file_parser.parse_file(file_path, is_stream)
        except Exception as e:
            logger.error("Failed to parse {}".format(file_path))
            logger.error("Error message: {}".format(e))
        return file_parser.ips

    def dir_handler(self, folder_path):
        """Handle parsing IP addresses from files recursively.

        Passes discovered files to the ``self.file_handler`` method for further
        processing.

        Args:
            folder_path (str): Directory path to recursively search for files.

        Return:
            data_dict (dict): dictionary of distinct IP addresses to resolve.
        """
        result_dict = {}
        for root, _, files in os.walk(folder_path):
            for fentry in files:
                file_entry = os.path.join(root, fentry)
                logger.debug("Parsing file {}".format(file_entry))
                file_results = self.file_handler(file_entry, self.ignore_bogon)
                logger.debug("Parsed file {}, {} results".format(
                    file_entry, len(file_results)))
                result_dict = dict(Counter(result_dict)+Counter(file_results))
        logger.debug("{} total distinct IPs discovered".format(
            len(result_dict)))
        return result_dict

    def resolve(self, data_dict, api_key=None):
        """Resolve IP addresses stored as keys within `data_dict`. The values
        for each key should represent the number of occurances of an IP within
        a data set.

        Args:
            data_dict (dict): Structured as ``{IP: COUNT}``
            api_key (str): API Key for GeoIP backend.

        Returns:
            data_dict (dict): dictionary of distinct IP addresses to resolve.
        """
        distinct_ips = list(data_dict.keys())

        if api_key:
            logger.debug("Using authenticated resolution service")
            resolver = ProResolver(api_key, fields=self.fields, lang=self.lang)
        else:
            resolver = Resolver(fields=self.fields, lang=self.lang)

        if self.pbar:
            resolver.pbar = self.pbar

        logger.debug("Resolving IPs")
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

        logger.debug("Resolved IPs")

        # Add frequency information to results
        if 'count' in self.fields:
            updated_results = []
            for result in results:
                query = str(result.get('query', ''))
                result['count'] = int(data_dict.get(query, '0'))
                updated_results.append(result)

            return updated_results
        return results

    def write_output(self, results):
        """Write results to output format and/or files.

        Leverages the writers found in libchickadee.backends. Currently
        supports csv, json, and json lines formats, specified in
        ``self.outformat``.

        Args:
            results (list): List of GeoIP results

        Returns:
            None
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


def setup_logging(path, verbose=False):  # pragma: no cover
    """Function to setup logging configuration

    Args:
        path (str): File path to write log messages to
        verbose (bool): If the debug messages should be displayed on STDERR

    Returns:
        None
    """
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


def config_handing(config_file=None, search_conf_path=[]):
    """Parse config file and return argument values.

    Args:
        config_file (str): Path to config file to read values from.
        search_conf_path (list): List of paths to look for config file

    Returns:
        dictionary containing configuration options.
    """

    # Field definitions
    # Set the default values here.
    section_defs = {
        'main': {
            'fields': '',
            'output-format': '',
            'progress': False,
            'no-resolve': False,
            'include-bogon': False,
            'log': '',
            'verbose': False
        },
        'backends': {
            'backend': {
                # Map backend to additional variables to pull.
                # For now, limited to api_key only.
                'ip_api': {'api-key': 'ip_api'}
            }
        }
    }

    if not config_file:
        if not search_conf_path:
            # Config file search path order:
            # 1. Current directory
            # 2. User home directory
            # 3. System wide directory
            # Needs to be named chickadee.ini or .chickadee.ini for detection.
            search_conf_path = [os.path.abspath('.'), os.path.expanduser('~')]
            if 'win32' in sys.platform:
                search_conf_path.append(
                    os.path.join(os.getenv('APPDATA'), 'chickadee'))
                search_conf_path.append('C:\\ProgramData\\chickadee')
            elif 'linux' in sys.platform or 'darwin' in sys.platform:
                search_conf_path.append(
                    os.path.expanduser('~/.config/chickadee'))
                search_conf_path.append('/etc/chickadee')

        for location in search_conf_path:
            if not os.path.exists(location) or not os.path.isdir(location):
                logger.debug(
                    "Unable to access config file location {}.".format(
                        location))
            elif 'chickadee.ini' in os.listdir(location):
                config_file = os.path.join(location, 'chickadee.ini')
            elif '.chickadee.ini' in os.listdir(location):
                config_file = os.path.join(location, '.chickadee.ini')

    fail_warn = 'Relying on argument defaults'
    if not config_file:
        logger.debug('Config file not found. ' + fail_warn)
        return

    if not os.path.exists(config_file) or not os.path.isfile(config_file):
        logger.debug('Error accessing config file ' + config_file + '.'
                     + fail_warn)
        return

    conf = configparser.ConfigParser()
    conf.read(config_file)

    config = {}

    for section in section_defs:
        if section in conf:
            for k, v in section_defs[section].items():
                conf_section = conf[section]
                conf_value = None
                if isinstance(v, str):
                    conf_value = conf_section.get(k)
                elif isinstance(v, list):
                    conf_value = conf_section.get(k).split(',')
                elif isinstance(v, bool):
                    conf_value = conf_section.getboolean(k)
                elif isinstance(v, dict):
                    conf_value = conf_section.get(k)
                    # Set backend args through nested option
                    for sk, sv, in v.get(conf_value, {}).items():
                        config[sk] = conf_section[sv]
                config[k] = conf_value

    return config


def arg_handling(args):
    """Parses command line arguments.

    Returns:
        argparse Namespace containing argument parameters.
    """
    parser = argparse.ArgumentParser(
        description=__desc__,
        formatter_class=CustomArgFormatter,
        epilog="Built by {}, v.{}".format(__author__, __version__)
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
    parser.add_argument('-n', '--no-resolve', action='store_true',
                        help="Only extract IP addresses, don't resolve.")
    parser.add_argument('-s', '--single',
                        help="Use the significantly slower single item API. "
                             "Adds reverse DNS.",
                        action='store_true')
    parser.add_argument('--lang', help="Language", default='en',
                        choices=['en', 'de', 'es', 'pt-BR', 'fr', 'ja',
                                 'zh-CN', 'ru'])
    parser.add_argument('-b', '--include-bogon', action='store_true',
                        help="Include BOGON addresses in results.")
    parser.add_argument('-c', '--config', help="Path to config file to load")
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
    return parser.parse_args(args)


def join_config_args(config, args, definitions={}):
    """Join config file and argument parameters, where the args override configs.

    Args:
        config (dict): Dictionary containing parameters from config file.
        args (obj): Argparse namespace containing command line parameters.
        definitions (dict): Dictionary of parameters to check for in args and
            config.

    Returns:
        (dict): Parameter information to use for script execution.
    """

    final_config = {}

    if not definitions:
        # This must match the defaults for argparse in order for the logic to
        # operate properly.
        definitions = {
            'fields': _FIELDS,
            'output-format': 'jsonl',
            'output-file': sys.stdout,
            'progress': False,
            'no-resolve': False,
            'include-bogon': False,
            'single': False,
            'lang': 'en',
            'log': os.path.abspath(os.path.join(
                os.getcwd(),
                PurePath(__file__).name.rsplit('.', 1)[0] + '.log')),
            'verbose': False,
            'backend': 'ip_api',
            'api-key': '',
            'data': ''
        }

    for k, v in definitions.items():
        args_val = getattr(args, k.replace('-', '_'), None)
        if config:
            config_val = config.get(k)
        else:
            config_val = None

        # Get from args if non-default
        if args_val != v and args_val is not None:
            final_config[k] = args_val

        # Special handling for API key
        elif k == 'api-key' and not config_val:
            final_config[k] = Chickadee.get_api_key()

        # Next get from config
        elif config_val:
            final_config[k] = config_val

        # Otherwise load from args if present
        elif args_val is not None:
            final_config[k] = args_val

        # And if all else fails, load from the definitions dictionary
        else:
            final_config[k] = v

    return final_config


def entry(args=sys.argv[1:]):  # pragma: no cover
    """Entrypoint for package script.

    Args:
        args: Arguments from invocation.
    """
    # Handle parameters from config file and command line.
    args = arg_handling(args)
    config = config_handing(args.config)
    params = join_config_args(config, args)

    # Check for update
    if update_available(__version__):
        sys.stderr.write(
            "Chickadee update is available. Please update "
            "using 'pip3 install --upgrade chickadee'.\n"
        )

    # Set up logging
    setup_logging(params.get('log'), params.get('verbose'))
    logger.debug("Starting Chickadee")
    for arg in vars(args):
        logger.debug("Argument {} is set to {}".format(
            arg, getattr(args, arg)
        ))

    logger.debug("Configuring Chickadee")
    chickadee = Chickadee(fields=params.get('fields').split(','))
    chickadee.resolve_ips = not params.get('no-resolve')
    chickadee.ignore_bogon = not params.get('include-bogon')
    chickadee.force_single = params.get('single')
    chickadee.lang = params.get('lang')
    chickadee.pbar = params.get('progress')

    logger.debug("Parsing input")
    if isinstance(params.get('data'), list):
        data = []
        for x in params.get('data'):
            res = chickadee.run(x, params.get('api-key', None))
            data += res
    else:
        data = chickadee.run(params.get('data'), params.get('api-key', None))

    logger.debug("Writing output")
    chickadee.outfile = params.get('output-file')
    chickadee.outformat = params.get('output-format')
    chickadee.write_output(data)

    logger.debug("Chickadee complete")


if __name__ == "__main__":
    entry()
