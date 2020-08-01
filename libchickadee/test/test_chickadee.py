"""Chickadee script tests."""
import unittest
import os
import sys
import io
from unittest.mock import patch

from libchickadee.chickadee import Chickadee, arg_handling, join_config_args, find_config_file
from libchickadee.chickadee import config_handing

__author__ = 'Chapin Bryce'
__date__ = 20200407
__license__ = 'MIT Copyright 2020 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''


class ChickadeeConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.default_columns = "query,message,mobile,org"
        
    def test_argparse(self):
        args = [
            "1.1.1.1", "-t", "csv", "-w", "test.out", "-n", "-s",
            "--lang", "es", "-c", "test.config", "-p", "-v",
            "--log", "test.log", "-f", self.default_columns
        ]
        parsed = arg_handling(args)

        self.assertEqual(parsed.data, ["1.1.1.1"])
        self.assertEqual(parsed.fields, self.default_columns)
        self.assertEqual(parsed.output_format, "csv")
        self.assertEqual(parsed.output_file, "test.out")
        self.assertEqual(parsed.lang, "es")
        self.assertEqual(parsed.config, "test.config")
        self.assertEqual(parsed.log, "test.log")
        self.assertTrue(parsed.no_resolve)
        self.assertTrue(parsed.single)
        self.assertTrue(parsed.progress)
        self.assertTrue(parsed.verbose)

        joined = join_config_args({}, parsed)
        self.assertDictEqual(
            joined,
            {
                "data": ["1.1.1.1"],
                "fields": self.default_columns,
                "lang": "es",
                "progress": True,
                'log': 'test.log',
                'verbose': True,
                'resolver': 'ip_api',
                'virustotal': '',
                'ip_api': '',
                'no-count': False,
                'no-resolve': True,
                'include-bogon': False,
                'single': True,
                'output-format': 'csv',
                'output-file': 'test.out'
            }
        )

    def test_configparse(self):
        args = ["1.1.1.1", "-f", self.default_columns]
        parsed = arg_handling(args)
        opts = {
            "fields": "query,message",
            "progress": True,
            "lang": "es"
        }
        joined = join_config_args(opts, parsed)

        self.assertDictEqual(
            joined,
            {
                "data": ["1.1.1.1"],
                "fields": self.default_columns,
                "lang": "es",
                "progress": True,
                'log': os.path.abspath(os.path.join(
                    os.getcwd(), 'chickadee.log')),
                'verbose': False,
                'resolver': 'ip_api',
                'ip_api': '',
                'virustotal': '',
                'no-count': False,
                'no-resolve': False,
                'include-bogon': False,
                'single': False,
                'output-format': 'jsonl',
                'output-file': sys.stdout,
            }
        )

    def test_parse_config_file_provided(self):
        # Str, list, bool, dict, int
        test_conf = 'chickadee.ini'
        open_file = open(test_conf, 'w')
        body = """
[main]
output-format = csv
verbose = true
fields = query,country
[resolvers]
resolver = ip_api
ip_api = not-an-api-key
        """
        open_file.write(body)
        open_file.close()
        data = config_handing(test_conf)
        self.assertDictEqual(
            data,
            {
                "output-format": "csv",
                "verbose": True,
                "fields": "query,country",
                "progress": None,
                "no-resolve": None,
                'include-bogon': None,
                "log": None,
                "resolver": "ip_api",
                'virustotal': None,
                "ip_api": "not-an-api-key"
            }
        )
        os.remove(test_conf)

    def test_find_config_file(self):
        # Str, list, bool, dict, int
        test_conf = 'unittesting.chickadee.ini'
        conf_path_userdir = os.path.join(
            os.path.expanduser("~"), test_conf)
        conf_path_workdir = os.path.abspath('unittesting.chickadee.ini')
        for conf_path in [conf_path_userdir, conf_path_workdir]:
            open_conf = open(conf_path, 'w')
            open_conf.close()
            actual = find_config_file(filename_patterns=["unittesting.chickadee.ini"])
            os.remove(conf_path)
            self.assertEqual(conf_path, actual)


class ChickadeeStringTestCase(unittest.TestCase):
    """Chickadee script tests."""
    def setUp(self):
        """Test config"""
        self.test_data_ips = [
            '10.0.1.2', '8.8.8.8', '2001:4860:4860::8888'
        ]
        self.expected_result = [
            {'query': '10.0.1.2', 'count': 1},

            {'as': 'AS15169 Google LLC', 'country': 'United States',
             'org': 'Level 3', 'proxy': False, 'query': '8.8.8.8', 'count': 1},

            {'as': 'AS15169 Google LLC', 'country': 'United States',
             'org': 'Google LLC', 'proxy': False, 'count': 1,
             'query': '2001:4860:4860::8888'}
        ]

        self.fields = ['query', 'count', 'as', 'country', 'org', 'proxy']

    def test_no_resolve(self, resolve='No resolve'):
        results = [
            {'query': '10.0.1.2', 'count': 1, 'message': resolve},
            {'query': '8.8.8.8', 'count': 1, 'message': resolve},
            {'query': '2001:4860:4860::8888', 'count': 1,
             'message': resolve}
        ]
        for count, ip in enumerate(self.test_data_ips):
            chickadee = Chickadee()
            chickadee.fields = self.fields
            chickadee.resolve_ips = False
            chickadee.ignore_bogon = False
            data = chickadee.run(ip)
            res = [x for x in data]
            self.assertEqual(res, [results[count]])

    @patch("libchickadee.resolvers.ipapi.Resolver.batch")
    def test_chickadee_single(self, mock_batch):
        """Query Method Test"""
        for count, ip in enumerate(self.test_data_ips):
            chickadee = Chickadee()
            chickadee.ignore_bogon = False
            chickadee.fields = self.fields
            mock_batch.return_value = [self.expected_result[count]]
            data = chickadee.run(ip)
            res = [x for x in data]
            self.assertEqual(res, [self.expected_result[count]])

    @patch("libchickadee.resolvers.ipapi.Resolver.batch")
    def test_chickadee_csv_str(self, mock_query):
        """Batch Query Method Test"""
        chickadee = Chickadee()
        chickadee.ignore_bogon = False
        chickadee.fields = self.fields
        mock_query.return_value = self.expected_result
        data = chickadee.run(','.join(self.test_data_ips))
        res = [x for x in data]
        self.assertCountEqual(res, self.expected_result)

    def test_chickadee_force_single(self):
        """Batch Query Method Test"""
        expected_results = self.expected_result

        class MockResolver:
            def __init__(self, *args, **kwargs):
                self.data = None

            def single(self):
                return [x for x in expected_results if x['query'] == self.data]

        chickadee = Chickadee()
        chickadee.ignore_bogon = False
        chickadee.force_single = True
        chickadee.fields = self.fields
        with patch("libchickadee.chickadee.ipapi.Resolver", MockResolver):
            data = chickadee.run(','.join(self.test_data_ips))
        res = [x for x in data]
        self.assertCountEqual(res, self.expected_result)

    def test_improper_type(self):
        failed = False
        try:
            # Provide improper data type
            Chickadee.str_handler(['test'])
        except TypeError:
            failed = True
        self.assertTrue(failed)

    @patch("libchickadee.resolvers.ipapi.Resolver.batch")
    def test_manual_run(self, mock_query):
        chick = Chickadee(fields=self.fields)
        mock_query.return_value = [self.expected_result[1]]
        actual = chick.run(self.test_data_ips[1])
        self.assertDictEqual(self.expected_result[1], actual[0])


class ChickadeeFileTestCase(unittest.TestCase):
    """Chickadee script tests."""
    def setUp(self):
        """Test setup."""
        self.test_data_dir = os.path.join(
            os.path.dirname(__file__), 'test_data')
        google_asn = "AS15169 Google LLC"
        usa = "United States"
        google_llc = "Google LLC"
        self.txt_data_results = [
            {"as": google_asn,
             "country": usa, "org": google_llc,
             "proxy": False, "query": "2001:4860:4860::8844",
             "count": 1},

            {"as": google_asn,
             "country": usa, "org": google_llc,
             "proxy": False, "query": "2001:4860:4860::8844",
             "count": 1},

            {"query": "10.0.1.2", "count": 1},

            {"as": google_asn,
             "country": usa, "org": "Level 3",
             "proxy": False, "query": "8.8.8.8", "count": 1},

            {"as": google_asn,
             "country": usa, "org": google_llc,
             "proxy": False, "query": "2001:4860:4860::8888",
             "count": 1},

            {"as": "AS3215 Orange S.A.",
             "country": "France", "org": "", "proxy": True,
             "query": "2.2.2.2", "count": 1},

            {"as": google_asn,
             "country": usa, "org": google_llc,
             "proxy": False, "query": "2001:4860:4860::8888", "count": 1},

            {"as": "AS3356 Level 3 Parent, LLC",
             "country": usa, "org": "Informs",
             "proxy": True, "query": "4.4.4.4", "count": 1},

            {"as": "AS13335 Cloudflare, Inc.",
             "country": "Australia", "org": "", "proxy": False,
             "query": "1.1.1.1", "count": 2}
        ]

        self.fields = ['query', 'count', 'as', 'country', 'org', 'proxy']

        self.xlsx_data_results = [
            {"as": google_asn,
             "country": usa, "org": google_llc,
             "proxy": False, "query": "2001:4860:4860::8844",
             "count": 2},

            {"query": "10.0.1.2", "count": 1},

            {"as": google_asn,
             "country": usa, "org": "Level 3",
             "proxy": False, "query": "8.8.8.8", "count": 1},

            {"as": google_asn,
             "country": usa, "org": google_llc,
             "proxy": False, "query": "2001:4860:4860::8888",
             "count": 1},

            {"as": "AS3215 Orange S.A.",
             "country": "France", "org": "", "proxy": True,
             "query": "2.2.2.2", "count": 1},

            {"as": "AS3356 Level 3 Parent, LLC",
             "country": usa, "org": "Informs",
             "proxy": True, "query": "4.4.4.4", "count": 1},

            {"as": "AS13335 Cloudflare, Inc.",
             "country": "Australia", "org": "", "proxy": False,
             "query": "1.1.1.1", "count": 2}
        ]

    @patch("libchickadee.resolvers.ipapi.Resolver.batch")
    def test_ipapi_resolve_query_txt_file(self, mock_query):
        """Batch Query Method Test"""
        chickadee = Chickadee()
        chickadee.ignore_bogon = False
        chickadee.fields = self.fields
        mock_query.return_value = self.txt_data_results
        data = chickadee.run(os.path.join(self.test_data_dir, 'txt_ips.txt'))
        res = [x for x in data]
        batch_result = []  # No reverse field
        for item in self.txt_data_results:
            batch_result.append(item)
        self.assertCountEqual(res, batch_result)

    @patch("libchickadee.resolvers.ipapi.Resolver.batch")
    def test_ipapi_resolve_query_gz_file(self, mock_query):
        """Batch Query Method Test"""
        chickadee = Chickadee()
        chickadee.ignore_bogon = False
        chickadee.fields = self.fields
        mock_query.return_value = self.txt_data_results
        data = chickadee.run(os.path.join(self.test_data_dir,
                                          'txt_ips.txt.gz'))
        res = [x for x in data]
        batch_result = []  # No reverse field
        for item in self.txt_data_results:
            batch_result.append(item)
        self.assertCountEqual(res, batch_result)

    @patch("libchickadee.resolvers.ipapi.Resolver.batch")
    def test_ipapi_resolve_query_xlsx_file(self, mock_query):
        """Batch Query Method Test"""
        chickadee = Chickadee()
        chickadee.ignore_bogon = False
        chickadee.fields = self.fields
        mock_query.return_value = self.xlsx_data_results
        data = chickadee.run(os.path.join(self.test_data_dir, 'test_ips.xlsx'))
        res = [x for x in data]
        batch_result = []  # No reverse field
        for item in self.xlsx_data_results:
            batch_result.append(item)
        self.assertCountEqual(res, batch_result)

    @patch("libchickadee.resolvers.ipapi.Resolver.batch")
    def test_ipapi_resolve_query_folder(self, mock_query):
        """Batch Query Method Test"""
        expected = [
            {"country": "Australia", "org": "",
             "as": "AS13335 Cloudflare, Inc.",
             "proxy": False, "query": "1.1.1.1", "count": 6},

            {"query": "10.0.1.2", "count": 3},

            {"country": "United States", "org": "Level 3",
             "as": "AS15169 Google LLC",
             "proxy": False, "query": "8.8.8.8", "count": 3},

            {"country": "United States", "org": "Google LLC",
             "as": "AS15169 Google LLC",
             "proxy": False, "query": "2001:4860:4860::8888", "count": 3},

            {"country": "United States", "org": "Informs",
             "as": "AS3356 Level 3 Parent, LLC", "proxy": True,
             "query": "4.4.4.4",
             "count": 3},

            {"country": "United States", "org": "Google LLC",
             "as": "AS15169 Google LLC",
             "proxy": False, "query": "2001:4860:4860::8844", "count": 4},

            {"country": "United States", "org": "Google LLC",
             "as": "AS15169 Google LLC",
             "proxy": False, "query": "2001:4860:4860::8888", "count": 3},

            {"country": "France", "org": "", "as": "AS3215 Orange S.A.",
             "proxy": True, "query": "2.2.2.2", "count": 3},

            {"country": "United States", "org": "Google LLC",
             "as": "AS15169 Google LLC",
             "proxy": False, "query": "2001:4860:4860::8844", "count": 4}
        ]
        mock_query.return_value = expected

        chickadee = Chickadee()
        chickadee.ignore_bogon = False
        chickadee.fields = self.fields
        data = chickadee.run(self.test_data_dir)
        res = [x for x in data]
        self.assertCountEqual(res, expected)

    def test_file_handler_stream(self):
        stream = io.TextIOWrapper(io.StringIO("test 1.1.1.1 ip"))
        ips = Chickadee.file_handler(stream, ignore_bogon=True)
        self.assertDictEqual(
            ips,
            {"1.1.1.1": 1}
        )


if __name__ == '__main__':
    unittest.main()
