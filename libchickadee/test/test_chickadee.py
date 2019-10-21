"""Chickadee script tests."""
import unittest
import os

from libchickadee.chickadee import Chickadee

__author__ = 'Chapin Bryce'
__date__ = 20190927
__license__ = 'GPLv3 Copyright 2019 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''

class ChickadeeStringTestCase(unittest.TestCase):
    """Chickadee script tests."""
    def setUp(self):
        """Test config"""
        self.test_data_ips = [
            '10.0.1.2', '8.8.8.8', '1.1.1.1', '2.2.2.2', '2001:4860:4860::8888'
        ]
        self.expected_result = [
            {'message': 'private range', 'query': '10.0.1.2'},

            {'as': 'AS15169 Google LLC', 'city': 'Ashburn',
             'country': 'United States', 'district': '', 'lat': 39.0438,
             'lon': -77.4874, 'mobile': False, 'org': 'Google LLC',
             'proxy': False, 'query': '8.8.8.8', 'reverse': 'dns.google',
             'regionName': 'Virginia', 'zip': '20149'},

            {'as': 'AS13335 Cloudflare, Inc.', 'city': 'Sydney',
             'country': 'Australia', 'district': '', 'lat': -33.8688,
             'lon': 151.209, 'mobile': False, 'org': '', 'proxy': False,
             'query': '1.1.1.1', 'regionName': 'New South Wales',
             'zip': '1001', 'reverse': 'one.one.one.one'},

            {'as': 'AS3215 Orange S.A.', 'city': 'Paris',
             'country': 'France', 'district': '', 'lat': 48.8566,
             'lon': 2.35222, 'mobile': False, 'org': '', 'proxy': True,
             'query': '2.2.2.2', 'regionName': 'Île-de-France',
             'zip': '75000', 'reverse': ''},

            {'as': 'AS15169 Google LLC', 'city': 'Ashburn',
             'country': 'United States', 'district': '', 'lat': 39.0438,
             'lon': -77.4874, 'mobile': False, 'org': 'Google LLC',
             'proxy': False, 'query': '2001:4860:4860::8888',
             'regionName': 'Virginia', 'zip': '20149',
             'reverse': 'dns.google',}
        ]

    def test_chickadee_single(self):
        """Query Method Test"""
        for count, ip in enumerate(self.test_data_ips):
            chickadee = Chickadee()
            data = chickadee.run(ip)
            res = [x for x in data]
            self.assertEqual(res, [self.expected_result[count]])

    def test_chickadee_csv_str(self):
        """Batch Query Method Test"""
        chickadee = Chickadee()
        data = chickadee.run(','.join(self.test_data_ips))
        res = [x for x in data]
        batch_result = [] # No reverse field
        for item in self.expected_result:
            if 'reverse' in item:
                item.pop('reverse')
            batch_result.append(item)
        self.assertCountEqual(res, batch_result)


class ChickadeeFileTestCase(unittest.TestCase):
    """Chickadee script tests."""
    def setUp(self):
        """Test setup."""
        self.test_data_dir = os.path.join(
            os.path.dirname(__file__), 'test_data')
        self.txt_data_results = [
            {"as": "AS15169 Google LLC", "city": "Ashburn",
             "country": "United States", "district": "", "lat": 39.0438,
             "lon": -77.4874, "mobile": False, "org": "Google LLC",
             "proxy": False, "query": "2001:4860:4860::8844",
             "regionName": "Virginia", "zip": "20149"},

            {"as": "AS15169 Google LLC", "city": "Ashburn",
             "country": "United States", "district": "", "lat": 39.0438,
             "lon": -77.4874, "mobile": False, "org": "Google LLC",
             "proxy": False, "query": "2001:4860:4860::8844",
             "regionName": "Virginia", "zip": "20149"},

            {"message": "private range", "query": "10.0.1.2"},

            {"as": "AS15169 Google LLC", "city": "Ashburn",
             "country": "United States", "district": "", "lat": 39.0438,
             "lon": -77.4874, "mobile": False, "org": "Google LLC",
             "proxy": False, "query": "8.8.8.8", "regionName": "Virginia",
             "zip": "20149"},

            {"as": "AS15169 Google LLC", "city": "Ashburn",
             "country": "United States", "district": "", "lat": 39.0438,
             "lon": -77.4874, "mobile": False, "org": "Google LLC",
             "proxy": False, "query": "2001:4860:4860::8888",
             "regionName": "Virginia", "zip": "20149"},

            {"as": "AS3215 Orange S.A.", "city": "Paris",
             "country": "France", "district": "", "lat": 48.8566,
             "lon": 2.35222, "mobile": False, "org": "", "proxy": True,
             "query": "2.2.2.2", "regionName": "\u00cele-de-France",
             "zip": "75000"},

            {"as": "AS15169 Google LLC", "city": "Ashburn",
             "country": "United States", "district": "", "lat": 39.0438,
             "lon": -77.4874, "mobile": False, "org": "Google LLC",
             "proxy": False, "query": "2001:4860:4860::8888", "regionName":
             "Virginia", "zip": "20149"},

            {"as": "AS3356 Level 3 Communications, Inc.",
             "city": "Minneapolis", "country": "United States",
             "district": "", "lat": 44.9778, "lon": -93.265, "mobile": False,
             "org": "Informs", "proxy": True, "query": "4.4.4.4",
             "regionName": "Minnesota", "zip": "55440"},

            {"as": "AS13335 Cloudflare, Inc.", "city": "Sydney",
             "country": "Australia", "district": "", "lat": -33.8688,
             "lon": 151.209, "mobile": False, "org": "", "proxy": False,
             "query": "1.1.1.1", "regionName": "New South Wales", "zip": "1001"}
        ]

        self.xlsx_data_results = [
            {"as": "AS15169 Google LLC", "city": "Ashburn",
             "country": "United States", "district": "", "lat": 39.0438,
             "lon": -77.4874, "mobile": False, "org": "Google LLC",
             "proxy": False, "query": "2001:4860:4860::8844",
             "regionName": "Virginia", "zip": "20149"},

            {"message": "private range", "query": "10.0.1.2"},

            {"as": "AS15169 Google LLC", "city": "Ashburn",
             "country": "United States", "district": "", "lat": 39.0438,
             "lon": -77.4874, "mobile": False, "org": "Google LLC",
             "proxy": False, "query": "8.8.8.8", "regionName": "Virginia",
             "zip": "20149"},

            {"as": "AS15169 Google LLC", "city": "Ashburn",
             "country": "United States", "district": "", "lat": 39.0438,
             "lon": -77.4874, "mobile": False, "org": "Google LLC",
             "proxy": False, "query": "2001:4860:4860::8888",
             "regionName": "Virginia", "zip": "20149"},

            {"as": "AS3215 Orange S.A.", "city": "Paris",
             "country": "France", "district": "", "lat": 48.8566,
             "lon": 2.35222, "mobile": False, "org": "", "proxy": True,
             "query": "2.2.2.2", "regionName": "\u00cele-de-France",
             "zip": "75000"},

            {"as": "AS3356 Level 3 Communications, Inc.",
             "city": "Minneapolis", "country": "United States",
             "district": "", "lat": 44.9778, "lon": -93.265, "mobile": False,
             "org": "Informs", "proxy": True, "query": "4.4.4.4",
             "regionName": "Minnesota", "zip": "55440"},

            {"as": "AS13335 Cloudflare, Inc.", "city": "Sydney",
             "country": "Australia", "district": "", "lat": -33.8688,
             "lon": 151.209, "mobile": False, "org": "", "proxy": False,
             "query": "1.1.1.1", "regionName": "New South Wales", "zip": "1001"}
        ]

    def test_ipapi_resolve_query_txt_file(self):
        """Batch Query Method Test"""
        chickadee = Chickadee()
        data = chickadee.run(os.path.join(self.test_data_dir, 'txt_ips.txt'))
        res = [x for x in data]
        batch_result = [] # No reverse field
        for item in self.txt_data_results:
            if 'reverse' in item:
                item.pop('reverse')
            batch_result.append(item)
        self.assertCountEqual(res, batch_result)

    def test_ipapi_resolve_query_gz_file(self):
        """Batch Query Method Test"""
        chickadee = Chickadee()
        data = chickadee.run(os.path.join(self.test_data_dir, 'txt_ips.txt.gz'))
        res = [x for x in data]
        batch_result = [] # No reverse field
        for item in self.txt_data_results:
            if 'reverse' in item:
                item.pop('reverse')
            batch_result.append(item)
        self.assertCountEqual(res, batch_result)

    def test_ipapi_resolve_query_xlsx_file(self):
        """Batch Query Method Test"""
        chickadee = Chickadee()
        data = chickadee.run(os.path.join(self.test_data_dir, 'test_ips.xlsx'))
        res = [x for x in data]
        batch_result = [] # No reverse field
        for item in self.xlsx_data_results:
            if 'reverse' in item:
                item.pop('reverse')
            batch_result.append(item)
        self.assertCountEqual(res, batch_result)

if __name__ == '__main__':
    unittest.main()
