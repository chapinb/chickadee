"""Chickadee script tests."""
import unittest
import os
import sys
import io

from libchickadee.chickadee import Chickadee, arg_handling, join_config_args
from libchickadee.chickadee import config_handing

__author__ = 'Chapin Bryce'
__date__ = 20200114
__license__ = 'MIT Copyright 2020 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''


class ChickadeeConfigTestCase(unittest.TestCase):
    def test_argparse(self):
        args = [
            "1.1.1.1", "-t", "csv", "-w", "test.out", "-n", "-s",
            "--lang", "es", "-c", "test.config", "-p", "-v",
            "--log", "test.log", "-f", "query,message,mobile,org"
        ]
        parsed = arg_handling(args)

        self.assertEqual(parsed.data, ["1.1.1.1"])
        self.assertEqual(parsed.fields, "query,message,mobile,org")
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
                "fields": "query,message,mobile,org",
                "lang": "es",
                "progress": True,
                'log': 'test.log',
                'verbose': True,
                'backend': 'ip_api',
                'api-key': None,
                'no-resolve': True,
                'include-bogon': False,
                'single': True,
                'output-format': 'csv',
                'output-file': 'test.out',
            }
        )

    def test_configparse(self):
        args = ["1.1.1.1", "-f", "query,message,mobile,org"]
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
                "fields": "query,message,mobile,org",
                "lang": "es",
                "progress": True,
                'log': os.path.abspath(os.path.join(
                    os.getcwd(), 'chickadee.log')),
                'verbose': False,
                'backend': 'ip_api',
                'api-key': None,
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
        [backends]
        backend = ip_api
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
                "backend": "ip_api",
                "api-key": "not-an-api-key"
            }
        )
        os.remove(test_conf)

    def test_parse_config_file_workdir(self):
        # Str, list, bool, dict, int
        test_conf = 'chickadee.ini'
        open_file = open(test_conf, 'w')
        body = """
        [main]
        output-format = csv
        verbose = true
        fields = query,country
        [backends]
        backend = ip_api
        ip_api = not-an-api-key
        """
        open_file.write(body)
        open_file.close()
        data = config_handing()
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
                "backend": "ip_api",
                "api-key": "not-an-api-key"
            }
        )
        os.remove(test_conf)

    def test_parse_config_file_userdir(self):
        # Str, list, bool, dict, int
        test_conf = '.chickadee.ini'
        conf_path = os.path.join(
            os.path.expanduser("~"), test_conf)
        open_file = open(conf_path, 'w')
        body = """
        [main]
        output-format = csv
        verbose = true
        fields = query,country
        [backends]
        backend = ip_api
        ip_api = not-an-api-key
        """
        open_file.write(body)
        open_file.close()
        data = config_handing()
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
                "backend": "ip_api",
                "api-key": "not-an-api-key"
            }
        )
        os.remove(conf_path)


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

    def test_no_resolve(self):
        results = [
            {'query': '10.0.1.2', 'count': 1, 'message': 'No resolve'},
            {'query': '8.8.8.8', 'count': 1, 'message': 'No resolve'},
            {'query': '2001:4860:4860::8888', 'count': 1,
             'message': 'No resolve'}
        ]
        for count, ip in enumerate(self.test_data_ips):
            chickadee = Chickadee()
            chickadee.fields = self.fields
            chickadee.resolve_ips = False
            chickadee.ignore_bogon = False
            data = chickadee.run(ip)
            res = [x for x in data]
            self.assertEqual(res, [results[count]])

    def test_chickadee_single(self):
        """Query Method Test"""
        for count, ip in enumerate(self.test_data_ips):
            chickadee = Chickadee()
            chickadee.ignore_bogon = False
            chickadee.fields = self.fields
            data = chickadee.run(ip)
            res = [x for x in data]
            self.assertEqual(res, [self.expected_result[count]])

    def test_chickadee_csv_str(self):
        """Batch Query Method Test"""
        chickadee = Chickadee()
        chickadee.ignore_bogon = False
        chickadee.fields = self.fields
        data = chickadee.run(','.join(self.test_data_ips))
        res = [x for x in data]
        self.assertCountEqual(res, self.expected_result)

    def test_chickadee_force_single(self):
        """Batch Query Method Test"""
        chickadee = Chickadee()
        chickadee.ignore_bogon = False
        chickadee.force_single = True
        chickadee.fields = self.fields
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


class ChickadeeFileTestCase(unittest.TestCase):
    """Chickadee script tests."""
    def setUp(self):
        """Test setup."""
        self.test_data_dir = os.path.join(
            os.path.dirname(__file__), 'test_data')
        self.txt_data_results = [
            {"as": "AS15169 Google LLC",
             "country": "United States", "org": "Google LLC",
             "proxy": False, "query": "2001:4860:4860::8844",
             "count": 1},

            {"as": "AS15169 Google LLC",
             "country": "United States", "org": "Google LLC",
             "proxy": False, "query": "2001:4860:4860::8844",
             "count": 1},

            {"query": "10.0.1.2", "count": 1},

            {"as": "AS15169 Google LLC",
             "country": "United States", "org": "Level 3",
             "proxy": False, "query": "8.8.8.8", "count": 1},

            {"as": "AS15169 Google LLC",
             "country": "United States", "org": "Google LLC",
             "proxy": False, "query": "2001:4860:4860::8888",
             "count": 1},

            {"as": "AS3215 Orange S.A.",
             "country": "France", "org": "", "proxy": True,
             "query": "2.2.2.2", "count": 1},

            {"as": "AS15169 Google LLC",
             "country": "United States", "org": "Google LLC",
             "proxy": False, "query": "2001:4860:4860::8888", "count": 1},

            {"as": "AS3356 Level 3 Communications, Inc.",
             "country": "United States", "org": "Informs",
             "proxy": True, "query": "4.4.4.4", "count": 1},

            {"as": "AS13335 Cloudflare, Inc.",
             "country": "Australia", "org": "", "proxy": False,
             "query": "1.1.1.1", "count": 2}
        ]

        self.fields = ['query', 'count', 'as', 'country', 'org', 'proxy']

        self.xlsx_data_results = [
            {"as": "AS15169 Google LLC",
             "country": "United States", "org": "Google LLC",
             "proxy": False, "query": "2001:4860:4860::8844",
             "count": 2},

            {"query": "10.0.1.2", "count": 1},

            {"as": "AS15169 Google LLC",
             "country": "United States", "org": "Level 3",
             "proxy": False, "query": "8.8.8.8", "count": 1},

            {"as": "AS15169 Google LLC",
             "country": "United States", "org": "Google LLC",
             "proxy": False, "query": "2001:4860:4860::8888",
             "count": 1},

            {"as": "AS3215 Orange S.A.",
             "country": "France", "org": "", "proxy": True,
             "query": "2.2.2.2", "count": 1},

            {"as": "AS3356 Level 3 Communications, Inc.",
             "country": "United States", "org": "Informs",
             "proxy": True, "query": "4.4.4.4", "count": 1},

            {"as": "AS13335 Cloudflare, Inc.",
             "country": "Australia", "org": "", "proxy": False,
             "query": "1.1.1.1", "count": 2}
        ]

    def test_ipapi_resolve_query_txt_file(self):
        """Batch Query Method Test"""
        chickadee = Chickadee()
        chickadee.ignore_bogon = False
        chickadee.fields = self.fields
        data = chickadee.run(os.path.join(self.test_data_dir, 'txt_ips.txt'))
        res = [x for x in data]
        batch_result = []  # No reverse field
        for item in self.txt_data_results:
            batch_result.append(item)
        self.assertCountEqual(res, batch_result)

    def test_ipapi_resolve_query_gz_file(self):
        """Batch Query Method Test"""
        chickadee = Chickadee()
        chickadee.ignore_bogon = False
        chickadee.fields = self.fields
        data = chickadee.run(os.path.join(self.test_data_dir,
                                          'txt_ips.txt.gz'))
        res = [x for x in data]
        batch_result = []  # No reverse field
        for item in self.txt_data_results:
            batch_result.append(item)
        self.assertCountEqual(res, batch_result)

    def test_ipapi_resolve_query_xlsx_file(self):
        """Batch Query Method Test"""
        chickadee = Chickadee()
        chickadee.ignore_bogon = False
        chickadee.fields = self.fields
        data = chickadee.run(os.path.join(self.test_data_dir, 'test_ips.xlsx'))
        res = [x for x in data]
        batch_result = []  # No reverse field
        for item in self.xlsx_data_results:
            batch_result.append(item)
        self.assertCountEqual(res, batch_result)

    def test_ipapi_resolve_query_folder(self):
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
             "as": "AS3356 Level 3 Communications, Inc.", "proxy": True,
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


class ChickadeeUtilityTestCase(unittest.TestCase):
    def test_get_apikey(self):
        os.environ["CHICKADEE_API_KEY"] = "test123"
        api_key = Chickadee.get_api_key()
        os.environ.pop("CHICKADEE_API_KEY")
        self.assertEqual(api_key, "test123")


if __name__ == '__main__':
    unittest.main()
