"""
ResolverBase
============

A base class for handling resolution of IP addresses.

This class includes elements common across resolver resolution data sources.
This includes common parameters, such as field names, and functions to handle
querying the data sources. Additionally, this includes writers for CSV and JSON
formats.

Module Documentation
--------------------
"""
import json
import csv

__author__ = 'Chapin Bryce'
__date__ = 20200107
__license__ = 'MIT Copyright 2020 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''


class ResolverBase:
    """Generic base class for use by other resolvers.

    Args:
        fields (list): Collection of fields to include in query.
        lang (str): Language for results.

    Returns:
        (ResolverBase)
    """
    def __init__(self):
        self.uri = None
        self.lang = 'en'
        self.supported_langs = []
        self.fields = []
        self.pbar = False  # Enable progress bars
        self.data = None

    def single(self):
        """Base method to handle single queries.

        Not implemented in base class.
        """
        raise NotImplementedError()

    def batch(self):
        """Base method to handle batch queries.

        Not implemented in base class."""
        raise NotImplementedError()

    def query(self, data):
        """Generic query handler to decide to use single or batch
            method for querying.

        Args:
            data (list, tuple, set, str): One or more IPs to resolve

        Returns:
            (list) List of collected records.

        Example:
            >>> records = ['1.1.1.1', '2.2.2.2']
            >>> resolver = ResolverBase()
            >>> resolved_data = resolver.query(records)
            >>> print(resolved_data)
            [
             {"query": "1.1.1.1", "country": "Australia", ...},
             {"query": "2.2.2.2", "country": "France", ...}
            ]
        """

        self.data = data
        if isinstance(data, (list, tuple, set)):
            return self.batch()
        if isinstance(data, str):
            return self.single()

        raise NotImplementedError()

    @staticmethod
    def defang_ioc(ioc):
        return ioc.replace(".", "[.]")

    @staticmethod
    def write_csv(outfile, data, headers=None):
        """Writes a list of dictionaries to a CSV file.

        Arguments:
            outfile (str or file_obj): Path to output file
            data (list): List of dictionaries to write to file
            headers (list): Header row to use. If empty, will use the
                first dictionary in the `data` list.

        Returns:
            None

        Example:
            >>> records = [{'query': '1.1.1.1', 'count': 2}]
            >>> resolver = ResolverBase()
            >>> resolver.write_csv('test.csv', records, ['query', 'count'])

        """

        if not headers:
            # Use the first line of data
            headers = [str(x) for x in data[0].keys()]

        # Write rows individually to handle flattening complex objects. Will update headers with new fields
        rows_to_write, headers = ResolverBase.flatten_objects(data, headers)

        was_opened = False
        if isinstance(outfile, str):
            open_file = open(outfile, 'w', newline="")
            was_opened = True
        else:
            open_file = outfile

        # Write only provided headers, ignore others
        csvfile = csv.DictWriter(open_file, headers,
                                 extrasaction='ignore')
        csvfile.writeheader()

        csvfile.writerows(rows_to_write)

        if was_opened:
            open_file.close()

    @staticmethod
    def write_json(outfile, data, headers=None, lines=False):
        """Writes output in JSON format

        Args:
            outfile (str or file_obj): Path to or already open file
            data (list): List of dictionaries containing resolved data
            headers (list): List of column headers. Will use the first element of data if not present.
            lines (bool): Whether to export 1 dictionary object per line or
                a whole json object.

        Returns:
            None

        Examples:
            Generation of a JSON report

            >>> records = [{'query': '1.1.1.1', 'count': 2}]
            >>> resolver = ResolverBase()
            >>> resolver.write_json('test.json', records, ['query', 'count'])

            Generation of a JSON Lines report

            >>> recs = [{'query': '1.1.1.1', 'count': 2}]
            >>> resolver = ResolverBase()
            >>> resolver.write_json('out.json', recs, ['query', 'count'], True)

        """
        was_opened = False
        open_file = outfile
        if isinstance(outfile, str):
            open_file = open(outfile, 'w', newline="")
            was_opened = True

        if headers:
            data = ResolverBase.normalize_data_headers(data, headers)

        if lines:
            for entry in data:
                open_file.write(json.dumps(entry)+"\n")
        else:
            open_file.write(json.dumps(data))

        if was_opened:
            open_file.close()

    @staticmethod
    def normalize_data_headers(data, headers):
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
        return selected_data

    @staticmethod
    def flatten_objects(data, headers):
        rows_to_write = []
        for raw_row in data:
            row = raw_row.copy()
            # Convert lists in to CSV friendly format
            for header in headers:
                if isinstance(raw_row.get(header, None), list):
                    # Converts list of simple values (str, int, float, bool) to pipe delimited string
                    row[header] = " | ".join(raw_row[header])
                elif isinstance(raw_row.get(header, None), dict):
                    # For each object in a dictionary, add a new header and append to
                    for key, value in raw_row[header].items():
                        new_header = '{}.{}'.format(header, key)
                        if new_header not in headers:
                            headers.append(new_header)
                        row[new_header] = value
            rows_to_write.append(row)
        return rows_to_write, headers
