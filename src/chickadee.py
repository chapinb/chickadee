"""Chickadee

An application to provide context for an IP address

"""

import argparse
import os
import json
import pprint
import time
import sys

import requests

from parsers.plain_text import PlainTextParser

__author__ = 'Chapin Bryce'
__date__ = 20190824
__license__ = 'GPLv3 Copyright 2019 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''

FIELDS = [ # Ordered list of fields to gather
            'query',
            'as', 'org', 'isp'
            'continent', 'country', 'regionName', 'city', 'district', 'zip',
            'mobile', 'proxy', 'reverse',
            'lat', 'lon', 'timezone'
            'status', 'message'
        ]


class Resolver(object):
    def __init__(self):
        self.uri = 'http://ip-api.com/'
        self.lang = "en"
        self.ratelimit = 150  # Requests per minute
        self.bulk_limit = 100  # Entries per request
        self.min_timeout = 60/self.ratelimit  # Minimum timeout period
        self.fields = [ # Ordered list of fields to gather
            'query',
            'as', 'org', 'isp'
            'continent', 'country', 'regionName', 'city', 'district', 'zip',
            'mobile', 'proxy', 'reverse',
            'lat', 'lon', 'timezone'
            'status', 'message'
        ]

        self.data = None
        self.last_req = time.time()

    def query(self, data):
        self.data = data
        if isinstance(data, (list, tuple, set)):
            return self.batch()
        elif isinstance(data, str):
            return self.single()
        else:
            raise NotImplementedError()

    def batch(self):
        records = []
        for ip in self.data:
            records.append({'query': ip})

        for x in range(0, len(records), 100):
            elapsed = time.time() - self.last_req
            if elapsed <= self.min_timeout and elapsed != 0:
                time.sleep(self.min_timeout - elapsed)
            rdata = requests.post(
                self.uri+"batch",
                json=records[x:x+100],
                params={
                    'fields': ','.join(self.fields),
                    'lang': self.lang
                })
            self.last_req = time.time()
            for result in rdata.json():
                yield result

    def single(self):
        elapsed = time.time() - self.last_req
        if elapsed <= self.min_timeout and elapsed != 0:
            time.sleep(self.min_timeout - elapsed)
        rdata = requests.get(
            self.uri+"json/"+self.data,
            params={
                'fields': ','.join(self.fields),
                'lang': self.lang
        })
        self.last_req = time.time()
        yield rdata.json()

def write_csv_dicts(outfile, data, headers=None):
    """Writes a list of dictionaries to a CSV file.

    Arguments:
        outfile (str): Path to output file
        data (list): List of dictionaries to write to file
        headers (list): Header row to use. If empty, will use the
            first dictionary in the `data` list.
    """

    if not headers:
        # Use the first line of data
        headers = [str(x) for x in data[0].keys()]

    if isinstance(outfile, str):
        open_file = open(outfile, 'w', newline="")
    else:
        open_file = outfile

    # Write only provided headers, ignore others
    csvfile = csv.DictWriter(open_file, headers,
                                extrasaction='ignore')
    csvfile.writeheader()
    csvfile.writerows(data)


def write_json(outfile, data, lines=False):
    if isinstance(outfile, str):
        open_file = open(outfile, 'w', newline="")
    else:
        open_file = outfile

    if lines:
        for entry in data:
            open_file.write(json.dumps(entry)+"\n")
    else:
        open_file.write(json.dumps(data))

def str_handler(input_data):
    if isinstance(input_data, str) and ',' in input_data:
        input_data = input_data.split(',')

    resolver = Resolver()
    if len(input_data) > resolver.bulk_limit * resolver.ratelimit:
        print("[!] Warning: due to rate limiting, this resolution will take "
              "at least {} minutes. Consider purchasing an API key for "
              "increased query performance".format(
                  len(input_data)/resolver.bulk_limit/resolver.ratelimit))
    results = resolver.query(input_data)
    all_results = [x for x in results]
    return all_results

def file_handler(input_data):
    print("Extracting IPs from files")
    ptparser = PlainTextParser()
    ptparser.parse_file(input_data)
    print("{} IPs discovered, resolving...".format(len(ptparser.ips)))
    return str_handler(list(ptparser.ips))


def dir_handler(input_data):
    ptparser = PlainTextParser()
    for root, _, files in os.walk(input_data):
        for fentry in files:
            ptparser.parse_file(os.path.join(root, fentry))
    return str_handler(list(ptparser.ips))


def main(input_data, outformat='json', outfile=None):
    """Evaluate the input data format and properly parse to extract and resolve
    IP addresses.

    Args:
        input_data (str or file_obj): User provided data containing IPs to
            resolve
    """

    if os.path.isdir(input_data):
        results = dir_handler(input_data) # Directory handler
    elif os.path.isfile(input_data):
        results = file_handler(input_data) # File handler
    elif isinstance(input_data, str):
        results = str_handler(input_data) # String handler

    if outformat == 'csv':
        write_csv_dicts(oufile, results)
    elif outformat == 'json':
        write_json(outfile, results)
    elif outformat == 'jsonl':
        write_json(outfile, results, lines=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Sample Argparse',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=f"Built by {__author__}, v.{__date__}"
    )
    parser.add_argument(
        'data',
        help="Either an IP address, comma delimited list of IP addresses, "
             "or path to a file or folder containing files to check for "
             "IP address values. Currently supported file types: "
             "plain text (ie logs, csv, json), gzipped plain text"
    )
    parser.add_argument('-f', help='Fields to query',
        default=FIELDS)
    parser.add_argument('-t', help='Output format',
                        choices=['json', 'jsonl', 'csv'],
                        default='jsonl')
    parser.add_argument('-w', help='Path to file to write output',
                        default=sys.stdout)
    args = parser.parse_args()

    main(args.data, outformat=args.t, outfile=args.w)
