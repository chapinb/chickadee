"""Chickadee script tests."""
import unittest
import os

from libchickadee.chickadee import Chickadee

__author__ = 'Chapin Bryce'
__date__ = 20200114
__license__ = 'GPLv3 Copyright 2019 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''


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
            data = chickadee.run(ip)
            res = [x for x in data]
            self.assertEqual(res, [results[count]])

    def test_chickadee_single(self):
        """Query Method Test"""
        for count, ip in enumerate(self.test_data_ips):
            chickadee = Chickadee()
            chickadee.fields = self.fields
            data = chickadee.run(ip)
            res = [x for x in data]
            self.assertEqual(res, [self.expected_result[count]])

    def test_chickadee_csv_str(self):
        """Batch Query Method Test"""
        chickadee = Chickadee()
        chickadee.fields = self.fields
        data = chickadee.run(','.join(self.test_data_ips))
        res = [x for x in data]
        self.assertCountEqual(res, self.expected_result)


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
        chickadee.fields = self.fields
        data = chickadee.run(os.path.join(self.test_data_dir, 'txt_ips.txt'))
        res = [x for x in data]
        batch_result = []  # No reverse field
        for item in self.txt_data_results:
            if 'reverse' in item:
                item.pop('reverse')
            batch_result.append(item)
        self.assertCountEqual(res, batch_result)

    def test_ipapi_resolve_query_gz_file(self):
        """Batch Query Method Test"""
        chickadee = Chickadee()
        chickadee.fields = self.fields
        data = chickadee.run(os.path.join(self.test_data_dir,
                                          'txt_ips.txt.gz'))
        res = [x for x in data]
        batch_result = []  # No reverse field
        for item in self.txt_data_results:
            if 'reverse' in item:
                item.pop('reverse')
            batch_result.append(item)
        self.assertCountEqual(res, batch_result)

    def test_ipapi_resolve_query_xlsx_file(self):
        """Batch Query Method Test"""
        chickadee = Chickadee()
        chickadee.fields = self.fields
        data = chickadee.run(os.path.join(self.test_data_dir, 'test_ips.xlsx'))
        res = [x for x in data]
        batch_result = []  # No reverse field
        for item in self.xlsx_data_results:
            if 'reverse' in item:
                item.pop('reverse')
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
        chickadee.fields = self.fields
        data = chickadee.run(self.test_data_dir)
        res = [x for x in data]
        self.assertCountEqual(res, expected)


if __name__ == '__main__':
    unittest.main()
