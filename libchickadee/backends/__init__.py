import json
import time
import csv

__author__ = 'Chapin Bryce'
__date__ = 20190907
__license__ = 'GPLv3 Copyright 2019 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''

class ResolverBase(object):
    def __init__(self):
        self.uri = None
        self.lang = "en"
        self.ratelimit = 100  # Requests per minute
        self.bulk_limit = 100  # Entries per request
        self.min_timeout = 60/self.ratelimit  # Minimum timeout
        self.fields = list() # Ordered list of fields to gather

        self.data = None
        self.last_req = time.time()

    def sleeper(self):
        elapsed = time.time() - self.last_req
        if elapsed <= self.min_timeout and elapsed != 0:
            time.sleep(self.min_timeout - elapsed)

    def single(self):
        """Base method to handle single queries"""
        pass

    def batch(self):
        """Base method to handle batch queries"""
        pass

    def query(self, data):
        """Generic query handler to decide to use single or batch
            method for querying."""
        self.data = data
        if isinstance(data, (list, tuple, set)):
            return self.batch()
        elif isinstance(data, str):
            return self.single()
        else:
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