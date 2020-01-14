"""Base class for all backends."""
import json
import csv

__author__ = 'Chapin Bryce'
__date__ = 20200107
__license__ = 'GPLv3 Copyright 2019 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''


class ResolverBase(object):
    """Generic base class for use by other backends."""
    def __init__(self, fields=list(), lang='en'):
        self.uri = None
        self.lang = lang
        self.supported_langs = []
        self.fields = fields  # Ordered list of fields to gather
        self.pbar = False  # Enable progress bars
        self.data = None

    def single(self):
        """Base method to handle single queries"""
        raise NotImplementedError()

    def batch(self):
        """Base method to handle batch queries"""
        raise NotImplementedError()

    def query(self, data):
        """Generic query handler to decide to use single or batch
            method for querying.

        Args:
            data (list, tuple,set or str): One or more IPs to resolve

        Return:
            (yield) request data iterator
        """
        self.data = data
        if isinstance(data, (list, tuple, set)):
            return self.batch()
        if isinstance(data, str):
            return self.single()

        raise NotImplementedError()

    @staticmethod
    def write_csv(outfile, data, headers=None):
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

    @staticmethod
    def write_json(outfile, data, headers=None, lines=False):
        """Writes output in JSON format

        Args:
            outfile (str or fileobj): Path to or already open file
            data (list): List of dictionaries containing resolved data
            lines (bool): Whether to export 1 dictionary object per line or
                a whole json object.
        """
        if isinstance(outfile, str):
            open_file = open(outfile, 'w', newline="")
        else:
            open_file = outfile

        if headers:
            # Only include fields in headers
            # Include headers with no value if not present in original
            selected_data = []
            for x in data:
                d = {}
                for k, v in x.items():
                    if k in headers:
                        d[k] = v
                for h in headers:
                    if h not in d:
                        d[h] = None
                selected_data.append(d)
            data = selected_data

        if lines:
            for entry in data:
                open_file.write(json.dumps(entry)+"\n")
        else:
            open_file.write(json.dumps(data))
