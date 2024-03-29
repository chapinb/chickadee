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

    usage: chickadee [-h] [-r {ip_api,virustotal}] [-f FIELDS]
                     [-t {json,jsonl,csv}] [-w FILENAME.JSON] [-n] [--no-count]
                     [-s] [--lang {en,de,es,pt-BR,fr,ja,zh-CN,ru}] [-b]
                     [-c CONFIG] [-p] [-v] [-V] [-l LOG]
                     [data [data ...]]

    Yet another GeoIP resolution tool.

    Will default to the free rate limited ip-api.com service for resolution.
    You can specify the paid API key for ip-api.com or for VirusTotal in
    the Chickadee configuration file. Please see template_chickadee.ini
    for more information.

    positional arguments:
      data                  Either an IP address, comma delimited list of IP addresses,
                            or path to a file or folder containing files to check for IP
                            address values. Currently supported file types: plain text
                            (ie logs, csv, json), gzipped plain text, xlsx
                            (must be xlsx extension). Can accept plain text data as
                            standard input.
                            (default: stdin)

    optional arguments:
      -h, --help            show this help message and exit
      -r {ip_api,virustotal}, --resolver {ip_api,virustotal}
                            Resolving service to use. Must specify api key in config file.
                            Please see template_chickadee.ini for instructions.
                            (default: ip_api)
      -f FIELDS, --fields FIELDS
                            Comma separated fields to query (default: None)
      -t {json,jsonl,csv}, --output-format {json,jsonl,csv}
                            Output format (default: jsonl)
      -w FILENAME.JSON, --output-file FILENAME.JSON
                            Path to file to write output
                            (default: stdout)
      -n, --no-resolve      Only extract IP addresses, don't resolve. (default: False)
      --no-count            Disable counting the occurrences of IP addresses extracted
                            from source files (default: False)
      -s, --single          Use the significantly slower single item API. Adds reverse
                            DNS. (default: False)
      --lang {en,de,es,pt-BR,fr,ja,zh-CN,ru}
                            Language (default: en)
      -b, --include-bogon   Include BOGON addresses in results. (default: False)
      -c CONFIG, --config CONFIG
                            Path to config file to load (default: None)
      -p, --progress        Enable progress bar (default: False)
      -v, --verbose         Include debug log messages (default: False)
      -V, --version         Displays version
      -l LOG, --log LOG     Path to log file (default: chickadee.log)

    Built by Chapin Bryce, v.20200805.0


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

Resolver options
^^^^^^^^^^^^^^^^

Resolve using VirusTotal (set API key in config file):

``chickadee -r virustotal 1.1.1.1``

Resolve using ip-api (set API key in config file):

``chickadee -r ip_api 1.1.1.1``

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

Changing the fields to resolve and report on (ip_api):

``chickadee -r ip_api -f query,count,asn,isp,org 1.1.1.1``

Changing the fields to resolve and report on (virustotal):

``chickadee -r virustotal -f query,detected_samples 1.1.1.1``

Changing the output location (STDOUT by default)

``chickadee 1.1.1.1 -w resolve.json``

Only extract IP addresses, don't resolve:

``chickadee -n 1.1.1.1``

Module Documentation
--------------------

"""

import argparse
import configparser
import logging
import os
import sys
from collections import Counter
from pathlib import PurePath

import _io
from tqdm import tqdm

# Import lib features
from libchickadee import __version__
from libchickadee.parsers.evtx import EVTXParser

# Import Parsers
from libchickadee.parsers.plain_text import PlainTextParser
from libchickadee.parsers.xlsx import XLSXParser

# Import resolvers
from libchickadee.resolvers import ResolverBase, ipapi, virustotal
from libchickadee.update import update_available

__author__ = "Chapin Bryce"
__date__ = 20200805
__license__ = "GPLv3 Copyright 2019 Chapin Bryce"
__desc__ = """Yet another GeoIP resolution tool.

Will default to the free rate limited ip-api.com service for resolution.
You can specify the paid API key for ip-api.com or for VirusTotal in
the Chickadee configuration file. Please see template_chickadee.ini
for more information.
"""

logger = logging.getLogger(__name__)


class CustomArgFormatter(
    argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter
):
    """Custom argparse formatter class"""


class Chickadee:
    """Class to handle chickadee script operations.

    Args:
        out_format (str): One of ``json``, ``jsonl``, ``csv``
        outfile (str or file_obj): Destination to write report.
        fields (list): Collection of fields to resolve and report on.

    Returns:
        None

    Examples:
        >>> chickadee = Chickadee()
        >>> resolution = chickadee.run('1.1.1.1')
        >>> print(resolution)

    """

    def __init__(self, out_format="json", outfile=sys.stdout, fields=None):
        """Initialize class values and parameters to provided or default values"""
        self.resolver = "ip_api"
        self.input_data = None
        self.out_format = out_format
        self.outfile = outfile
        self.fields = fields
        self.force_single = False
        self.ignore_bogon = True
        self.no_count = False
        self.lang = "en"
        self.progress_bar = False
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
            api_key (str): API Key for IP resolver.

        Returns:
            (list): List of dictionaries containing resolved hits.
        """
        self.input_data = input_data
        result_dict = {}
        # Extract and resolve IP addresses
        if not isinstance(self.input_data, _io.TextIOWrapper) and os.path.isdir(
            self.input_data
        ):
            logger.debug("Detected the data source as a directory")
            result_dict = self.dir_handler(self.input_data)  # Dir handler

        elif isinstance(self.input_data, _io.TextIOWrapper) or os.path.isfile(
            self.input_data
        ):
            logger.debug("Detected the data source as a file")
            # File handler
            result_dict = self.file_handler(self.input_data, self.ignore_bogon)

        elif isinstance(self.input_data, str):
            logger.debug("Detected the data source as raw value(s)")
            result_dict = self.str_handler(self.input_data)  # String handler

        logger.debug("Extracted %s distinct IPs", len(list(result_dict.keys())))

        # Resolve if requested
        if self.resolve_ips:
            return self.resolve(result_dict, api_key)

        return [
            {"query": k, "count": v, "message": "No resolve"}
            for k, v in result_dict.items()
        ]

    @staticmethod
    def get_api_key():
        """DEPRECIATED

        Retrieve an API key set as an environment variable. Looks for value in
        ``CHICKADEE_API_KEY``. May be depreciated in the near future.

        Returns:
            (str): API key, if found
        """
        raise NotImplementedError(
            "Please use a configuration file to specify the API key"
        )

    @staticmethod
    def str_handler(data):
        """Handle string input of one or more IP addresses and returns the
        distinct IPs with their associated frequency count.

        Args:
            data (list, str): raw input data from user

        Return:
            data_dict (dict): dictionary of distinct IP addresses to resolve.
        """
        if isinstance(data, str) and "," in data:
            # List of IPs
            raw_data = data.strip().split(",")
        elif isinstance(data, str):
            # Single IP
            raw_data = [data.strip()]
        else:
            raise TypeError("Unsupported input provided.")

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
            logger.debug("Extracting IPs from %s", file_path)

        if not is_stream and file_path.lower().endswith("xlsx"):
            file_parser = XLSXParser(ignore_bogon)
        elif not is_stream and file_path.lower().endswith("evtx"):
            file_parser = EVTXParser(ignore_bogon)
        else:
            file_parser = PlainTextParser(ignore_bogon)
        try:
            file_parser.parse_file(file_path, is_stream)
        except Exception as e:
            logger.error("Failed to parse %s", file_path)
            logger.error("Error message: %s", e)
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
            for file_name in files:
                file_entry = os.path.join(root, file_name)
                logger.debug("Parsing file %s", file_entry)
                file_results = self.file_handler(file_entry, self.ignore_bogon)
                logger.debug(
                    "Parsed file %s, %s results", file_entry, len(file_results)
                )
                result_dict = dict(Counter(result_dict) + Counter(file_results))
        logger.debug("%s total distinct IPs discovered", len(result_dict))
        return result_dict

    def resolve(self, data_dict, api_key=None):
        """Resolve IP addresses stored as keys within `data_dict`. The values
        for each key should represent the number of occurrences of an IP within
        a data set.

        Args:
            data_dict (dict): Structured as ``{IP: COUNT}``
            api_key (str): API Key for IP resolver.

        Returns:
            results (list): List containing resolved IP address information
        """
        distinct_ips = list(data_dict.keys())

        resolver = self.get_resolver(api_key)

        if self.progress_bar:
            resolver.pbar = self.progress_bar

        logger.debug("Resolving IPs")
        if self.force_single:
            results = []
            data = distinct_ips
            if self.progress_bar:
                data = tqdm(distinct_ips, desc="Resolving IPs", unit_scale=True)

            for element in data:
                resolver.data = element
                results += resolver.single()
        else:
            results = resolver.query(distinct_ips)

        logger.debug("Resolved IPs")

        # Add frequency information to results
        if not self.no_count:
            updated_results = []
            for result in results:
                query = str(result.get("query", ""))
                # noinspection PyTypeChecker
                result["count"] = int(data_dict.get(query, "0"))
                updated_results.append(result)

            return updated_results
        return results

    def get_resolver(self, api_key):
        """Determine the proper resolver to use, based on the available API keys.

        Args:
            api_key (str): API key value to register with the resolver

        Returns:
            Instance of an initialized resolver
        """
        resolvers = {
            "ip_api": {
                "pro_resolver": ipapi.ProResolver,
                "free_resolver": ipapi.Resolver,
            },
            "virustotal": {
                "pro_resolver": virustotal.ProResolver,
                "free_resolver": None,
            },
        }

        if api_key:
            logger.debug("Using authenticated resolution service")
            resolver_class = resolvers[self.resolver]["pro_resolver"]
            if not resolver_class:
                raise ValueError(
                    "Unable to configure resolver. Please report to github.com/chapinb/chickadee/issues"
                )
            resolver = resolver_class(api_key, fields=self.fields, lang=self.lang)
            logger.debug("Resolver API key found.")
        elif resolver_class := resolvers[self.resolver]["free_resolver"]:
            resolver = resolver_class(fields=self.fields, lang=self.lang)

        else:
            raise ValueError(
                f"Unable to configure resolver. An API key may be required for {self.resolver}"
            )
        if not self.fields:
            # Inherit the fields used by the resolver if none are used.
            self.fields = resolver.fields

        return resolver

    def write_output(self, results):
        """Write results to output format and/or files.

        Leverages the writers found in libchickadee.resolvers. Currently
        supports csv, json, and json lines formats, specified in
        ``self.out_format``.

        Args:
            results (list): List of GeoIP results

        Returns:
            None
        """

        if self.out_format == "csv":
            logger.debug("Writing CSV report")
            ResolverBase.write_csv(self.outfile, results, self.fields)
        elif self.out_format == "json":
            logger.debug("Writing json report")
            ResolverBase.write_json(self.outfile, results, self.fields)
        elif self.out_format == "jsonl":
            logger.debug("Writing json lines report")
            ResolverBase.write_json(self.outfile, results, self.fields, lines=True)


def setup_logging(logging_obj, log_file, verbose=False):
    """Function to setup logging configuration and test it.

    Args:
        logging_obj: A logging instance, returned from logging.getLogger().
        log_file: File path to write log messages to.
        verbose: Whether or not to enable the debug level in STDERR output.
    """
    logging_obj.setLevel(logging.DEBUG)

    # Logging formatter. Best to keep consistent for most use cases
    log_format = logging.Formatter(
        "%(asctime)s %(filename)s %(levelname)s %(module)s "
        "%(funcName)s %(lineno)d %(message)s"
    )

    # Setup STDERR logging, allowing you uninterrupted
    # STDOUT redirection
    stderr_handle = logging.StreamHandler(stream=sys.stderr)
    if verbose:
        stderr_handle.setLevel(logging.DEBUG)
    else:
        stderr_handle.setLevel(logging.INFO)
    stderr_handle.setFormatter(log_format)

    # Setup file logging
    file_handle = logging.FileHandler(log_file, "a")
    file_handle.setLevel(logging.DEBUG)
    file_handle.setFormatter(log_format)

    # Add handles
    logging_obj.addHandler(stderr_handle)
    logging_obj.addHandler(file_handle)


def config_handing(config_file=None, search_conf_path=None):
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
        "main": {
            "fields": "",
            "output-format": "",
            "progress": False,
            "no-resolve": False,
            "include-bogon": False,
            "log": "",
            "verbose": False,
        },
        "resolvers": {
            "resolver": "",
            "ip_api": "",  # Hold respective API key
            "virustotal": "",  # Hold respective API key
        },
    }

    if not config_file:
        config_file = find_config_file(search_conf_path)

    fail_warn = "Relying on argument defaults"
    if not config_file:
        logger.debug("Config file not found. %s", fail_warn)
        return

    if not (os.path.exists(config_file) and os.path.isfile(config_file)):
        logger.debug("Error accessing config file %s. %s", config_file, fail_warn)
        return

    conf = configparser.ConfigParser()
    conf.read(config_file)

    return parse_config_sections(conf, section_defs)


def parse_config_sections(conf, section_defs):
    """Parse the sections of the configuration file

    Args:
        conf (dict): Loaded configuration file information
        section_defs (dict): Mapping of configuration file values and defaults

    Returns:
        (dict): Final configuration to use with the script execution
    """
    config = {}
    for section, value in section_defs.items():
        if section not in conf:
            continue
        for k, v in value.items():
            conf_section = conf[section]
            conf_value = None
            if isinstance(v, str):
                conf_value = conf_section.get(k)
            elif isinstance(v, list):
                conf_value = conf_section.get(k).split(",")
            elif isinstance(v, bool):
                conf_value = conf_section.getboolean(k)
            elif isinstance(v, dict):
                raise NotImplementedError(
                    "Unable to parse dictionary objects from config file mapping"
                )
            config[k] = conf_value
    return config


def find_config_file(search_conf_path=None, filename_patterns=None):
    """Handles the search operations for identifying configuration files on the system

    Args:
        search_conf_path (str): Path to look for a configuration file
        filename_patterns (list): Patterns to use to find a configuration file

    Returns:
        (str): The path to the first identified configuration file.
    """
    if not filename_patterns:
        # Needs to end with chickadee.ini or .chickadee.ini for detection.
        filename_patterns = ["chickadee.ini"]

    if not search_conf_path:
        search_conf_path = _generate_default_config_search_path()

    for location in search_conf_path:
        if not (os.path.exists(location) and os.path.isdir(location)):
            logger.debug("Unable to access config file location %s.", location)
            continue
        for file_name in os.listdir(location):
            for pattern in filename_patterns:
                if file_name.endswith(pattern):
                    return os.path.join(location, file_name)


def _generate_default_config_search_path():
    """This function dynamically populates the order in which to locate a configuration file.

    Config file search path order:
      1. Current directory
      2. User home directory
      3. System wide directory

    Returns:
        (list): Ordered list of paths to look for configuration files in
    """
    search_conf_path = [os.path.abspath("."), os.path.expanduser("~")]
    if "win32" in sys.platform:
        search_conf_path.extend(
            (
                os.path.join(os.getenv("APPDATA"), "chickadee"),
                "C:\\ProgramData\\chickadee",
            )
        )
    elif "linux" in sys.platform or "darwin" in sys.platform:
        search_conf_path.extend(
            (os.path.expanduser("~/.config/chickadee"), "/etc/chickadee")
        )
    return search_conf_path


def arg_handling(args):
    """Parses command line arguments.

    Returns:
        argparse Namespace containing argument parameters.
    """
    # noinspection PyTypeChecker
    parser = argparse.ArgumentParser(
        description=__desc__,
        formatter_class=CustomArgFormatter,
        epilog=f"Built by {__author__}, v.{__version__}",
    )
    parser.add_argument(
        "data",
        help="Either an IP address, comma delimited list of IP addresses, "
        "or path to a file or folder containing files to check for "
        "IP address values. Currently supported file types: "
        "plain text (ie logs, csv, json), gzipped plain text, xlsx "
        "(must be xlsx extension). Can accept plain text data as stdin.",
        nargs="*",
        default=sys.stdin,
    )
    parser.add_argument(
        "-r",
        "--resolver",
        help="Resolving service to use. Must specify api key in config file. "
        "Please see template_chickadee.ini for instructions.",
        choices=["ip_api", "virustotal"],
        default="ip_api",
    )
    parser.add_argument("-f", "--fields", help="Comma separated fields to query")
    parser.add_argument(
        "-t",
        "--output-format",
        help="Output format",
        choices=["json", "jsonl", "csv"],
        default="jsonl",
    )
    parser.add_argument(
        "-w",
        "--output-file",
        help="Path to file to write output",
        default=sys.stdout,
        metavar="FILENAME.JSON",
    )
    parser.add_argument(
        "-n",
        "--no-resolve",
        action="store_true",
        help="Only extract IP addresses, don't resolve.",
    )
    parser.add_argument(
        "--no-count",
        action="store_true",
        help="Disable counting the occurrences of IP addresses extracted from source files",
    )
    parser.add_argument(
        "-s",
        "--single",
        help="Use the significantly slower single item API. Adds reverse DNS.",
        action="store_true",
    )
    parser.add_argument(
        "--lang",
        help="Language",
        default="en",
        choices=["en", "de", "es", "pt-BR", "fr", "ja", "zh-CN", "ru"],
    )
    parser.add_argument(
        "-b",
        "--include-bogon",
        action="store_true",
        help="Include BOGON addresses in results.",
    )
    parser.add_argument("-c", "--config", help="Path to config file to load")
    parser.add_argument(
        "-p", "--progress", help="Enable progress bar", action="store_true"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Include debug log messages"
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        help="Displays version",
        version=str(__version__),
    )
    parser.add_argument(
        "-l",
        "--log",
        help="Path to log file",
        default=os.path.abspath(
            os.path.join(
                os.getcwd(), PurePath(__file__).name.rsplit(".", 1)[0] + ".log"
            )
        ),
    )
    return parser.parse_args(args)


def join_config_args(config, args, definitions=None):
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
            "fields": "",
            "output-format": "jsonl",
            "output-file": sys.stdout,
            "progress": False,
            "no-resolve": False,
            "no-count": False,
            "include-bogon": False,
            "single": False,
            "lang": "en",
            "log": os.path.abspath(
                os.path.join(
                    os.getcwd(), PurePath(__file__).name.rsplit(".", 1)[0] + ".log"
                )
            ),
            "verbose": False,
            "resolver": "ip_api",
            "ip_api": "",  # Hold the related API key
            "virustotal": "",  # Hold the related API key
            "data": "",
        }

    for k, v in definitions.items():
        args_val = getattr(args, k.replace("-", "_"), None)
        config_val = config.get(k) if config else None

        # Get from args if non-default
        if args_val != v and args_val is not None:
            final_config[k] = args_val

        # Next get from the config
        elif config_val:
            final_config[k] = config_val

        # Otherwise load from args if present
        elif args_val is not None:
            final_config[k] = args_val

        else:
            final_config[k] = v

    return final_config


def entry(args=None):  # pragma: no cover
    """Entrypoint for package script.

    Args:
        args: Arguments from invocation.
    """
    if not args:
        args = sys.argv[1:]
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
    setup_logging(logger, params.get("log"), params.get("verbose"))
    logger.debug("Starting Chickadee")
    for arg in vars(args):
        logger.debug("Argument %s is set to %s", arg, getattr(args, arg))

    logger.debug("Configuring Chickadee")
    fields = (
        params.get("fields", "").split(",")
        if len(params.get("fields", "")) > 0
        else None
    )
    chickadee = Chickadee(fields=fields)
    chickadee.resolver = params.get("resolver", "ip_api")
    chickadee.resolve_ips = not params.get("no-resolve")
    chickadee.ignore_bogon = not params.get("include-bogon")
    chickadee.no_count = params.get("no-count")
    chickadee.force_single = params.get("single")
    chickadee.lang = params.get("lang")
    chickadee.progress_bar = params.get("progress")

    logger.debug("Parsing input")
    if isinstance(params.get("data"), list):
        data = []
        for x in params.get("data"):
            res = chickadee.run(x, params.get(chickadee.resolver))
            data += res
    else:
        data = chickadee.run(params.get("data"), params.get(chickadee.resolver))

    logger.debug("Writing output")
    chickadee.outfile = params.get("output-file")
    chickadee.out_format = params.get("output-format")
    chickadee.write_output(data)

    logger.debug("Chickadee complete")


if __name__ == "__main__":
    entry()
