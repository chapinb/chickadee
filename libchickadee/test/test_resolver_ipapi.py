"""IP-API Resolver Tests."""
import unittest
from datetime import datetime
from unittest.mock import patch
import csv
import json
import os
from collections import OrderedDict

from libchickadee.resolvers.ipapi import Resolver

__author__ = 'Chapin Bryce'
__date__ = 20200114
__license__ = 'MIT Copyright 2020 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''


class MockResponse:
    def __init__(self, json_data, status_code, rl='100', ttl='1'):
        self.run_count = 0
        self.json_data = json_data
        self.status_code = status_code
        self.headers = {'X-Rl': rl, 'X-Ttl': ttl}

    def json(self):
        return self.json_data


class IPAPITestCase(unittest.TestCase):
    """IP-API Resolver Tests."""
    def setUp(self):
        """Test config"""
        self.test_data_ips = [
            '10.0.1.2', '8.8.8.8', '2001:4860:4860::8888'
        ]
        self.expected_result = [
            {'query': '10.0.1.2'},

            {'as': 'AS15169 Google LLC', 'country': 'United States',
             'org': 'Level 3', 'proxy': False, 'query': '8.8.8.8'},

            {'as': 'AS15169 Google LLC', 'country': 'United States',
             'org': 'Google LLC', 'proxy': False,
             'query': '2001:4860:4860::8888'}
        ]
        self.resolver = Resolver(fields=['query', 'count', 'as',
                                         'country', 'org', 'proxy'])

    @patch("libchickadee.resolvers.ipapi.Resolver.single")
    def test_ipapi_resolve_query_single(self, mock_query):
        """Query Method Test"""
        for count, ip in enumerate(self.test_data_ips):
            mock_query.return_value = self.expected_result[count]
            data = self.resolver.query(ip)
            self.assertEqual(data, self.expected_result[count])

    @patch("libchickadee.resolvers.ipapi.Resolver.batch")
    def test_ipapi_resolve_query_batch(self, mock_query):
        """Batch Query Method Test"""
        mock_query.return_value = self.expected_result.copy()
        data = self.resolver.query(self.test_data_ips)
        res = [x for x in data]
        batch_result = []  # No reverse field
        for item in self.expected_result:
            batch_result.append(item)
        self.assertCountEqual(res, batch_result)

    @patch("libchickadee.resolvers.ipapi.requests.get")
    def test_ipapi_resolve_single(self, mock_query):
        """Single Query Method Test"""
        for count, ip in enumerate(self.test_data_ips):
            mock_query.return_value = MockResponse(json_data=self.expected_result[count], status_code=200)
            self.resolver.data = ip
            data = self.resolver.single()
            self.assertEqual(data, [self.expected_result[count]])

    @patch("libchickadee.resolvers.ipapi.requests.post")
    def test_ipapi_resolve_batch(self, mock_query):
        """Batch Query Method Test"""
        mock_query.return_value = MockResponse(json_data=self.expected_result, status_code=200)
        self.resolver.data = self.test_data_ips
        data = self.resolver.batch()
        res = [x for x in data]
        self.assertEqual(len(res), len(self.expected_result))

    @patch("libchickadee.resolvers.ipapi.Resolver.single")
    def test_ipapi_resolve_single_field(self, mock_query):
        """Single Query Method Test"""
        for count, ip in enumerate(self.test_data_ips):
            expected = {
                'query': self.expected_result[count].get('query', None),
                'country': self.expected_result[count].get('country', None),
                'as': self.expected_result[count].get('as', None),
            }

            mock_query.return_value = expected
            self.resolver.data = ip
            self.resolver.fields = ['query', 'country', 'as']
            data = self.resolver.single()

            self.assertEqual(data, expected)

    @patch("libchickadee.resolvers.ipapi.requests.get")
    @patch("libchickadee.resolvers.ipapi.requests.post")
    def test_ipapi_rate_limiting(self, mock_get, mock_post):
        single = {
            "test_data": self.test_data_ips[1],
            "expected_data": [self.expected_result[1]],
            "mock_data": [
                MockResponse(json_data={}, status_code=429, rl='0', ttl='2'),
                MockResponse(json_data=self.expected_result[1], status_code=200, rl='0', ttl='0')
            ]
        }
        batch = {
            "test_data": self.test_data_ips,
            "expected_data": self.expected_result,
            "mock_data": [
                MockResponse(json_data={}, status_code=429, rl='0', ttl='2'),
                MockResponse(json_data=self.expected_result, status_code=200, rl='0', ttl='0')
            ]
        }
        for test in [single, batch]:
            test_ip = test['test_data']
            mock_get.side_effect = test['mock_data']
            mock_post.side_effect = test['mock_data']
            start_time = datetime.now()
            data = self.resolver.query(test_ip)
            delta = datetime.now() - start_time
            self.assertTrue(delta.total_seconds() > 1)
            self.assertEqual(data, test['expected_data'])


class WritersTestCase(unittest.TestCase):
    def setUp(self):
        self.data = [
            OrderedDict(**{"a": '1', "b": "2"})
        ]
        self.testfile = "testfile"
        self.open_file = None

    def tearDown(self):
        self.open_file.close()
        os.remove(self.testfile)

    def test_write_csv(self):
        Resolver.write_csv(self.testfile, self.data)
        self.open_file = open("testfile")
        read_data = next(csv.DictReader(self.open_file))
        self.assertDictEqual(
            self.data[0],
            read_data
        )

    def test_write_json(self):
        data = [
            {"a": '1', "b": "2"}
        ]
        Resolver.write_json(self.testfile, self.data)
        self.open_file = open("testfile")
        read_data = json.load(self.open_file)
        self.assertEqual(
            data,
            read_data
        )

    def test_write_json_headers(self):
        Resolver.write_json(self.testfile, self.data, ['a', 'none'])
        self.open_file = open("testfile")
        read_data = json.load(self.open_file)
        rec = self.data[0]
        rec.pop("b")
        rec["none"] = None
        self.assertDictEqual(
            rec,
            read_data[0]
        )

    def test_write_json_lines(self):
        Resolver.write_json(self.testfile, self.data, lines=True)
        self.open_file = open("testfile")
        read_data = json.load(self.open_file)
        self.assertDictEqual(
            self.data[0],
            read_data
        )


if __name__ == '__main__':
    unittest.main()
