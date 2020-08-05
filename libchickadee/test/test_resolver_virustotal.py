"""VirusTotal Resolver Tests."""
import datetime
import time
import unittest
import json
import os
from unittest.mock import patch, MagicMock

from libchickadee.resolvers.virustotal import ProResolver

__author__ = 'Chapin Bryce'
__date__ = 20200805
__license__ = 'MIT Copyright 2020 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''


class IPAPITestCase(unittest.TestCase):
    """VirusTotal Resolver Tests."""
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
        self.resolver = ProResolver(api_key='')
        local_dir = os.path.abspath(__file__).rsplit(os.sep, 1)[0]
        resource_file = open(os.path.join(local_dir, 'vt_resp_data.json'))
        self.vt_rep_data_list = json.load(resource_file)
        resource_file.close()

    def test_parse_vt_resp(self):
        vt_resp_data = self.vt_rep_data_list["Test0"]["test"]
        query = self.vt_rep_data_list["Test0"]["query"]
        expected = self.vt_rep_data_list["Test0"]["expected"]
        vt_values = self.resolver.parse_vt_resp(query, vt_resp_data)
        self.assertDictEqual(expected, vt_values)

    def test_parse_vt_resp_2(self):
        vt_resp_data = self.vt_rep_data_list["Test1"]["test"]
        query = self.vt_rep_data_list["Test1"]["query"]
        expected = self.vt_rep_data_list["Test1"]["expected"]
        vt_values = self.resolver.parse_vt_resp(query, vt_resp_data)
        self.assertDictEqual(expected, vt_values)

    @patch("libchickadee.resolvers.virustotal.requests.get")
    def test_resolve_single(self, mock_requests):
        def mock_json():
            return self.vt_rep_data_list["Test0"]["test"]

        mock_requests.return_value.status_code = 200
        mock_requests.return_value.json = mock_json
        actual = self.resolver.query(self.vt_rep_data_list["Test0"]["query"])
        expected = self.vt_rep_data_list["Test0"]["expected"]
        self.assertEqual(1, len(actual))
        self.assertDictEqual(expected, actual[0])

    @patch("libchickadee.resolvers.virustotal.requests.get")
    def test_resolve_batch(self, mock_requests):
        # Build 3 requests
        req1 = MagicMock()
        req1.status_code = 200
        req1.json = lambda: self.vt_rep_data_list["Test0"]["test"]

        req2 = MagicMock()
        req2.status_code = 204

        req3 = MagicMock()
        req3.status_code = 200
        req3.json = lambda: self.vt_rep_data_list["Test1"]["test"]

        mock_requests.side_effect = [req1, req2, req3]
        start = datetime.datetime.now()
        actual = self.resolver.query([self.vt_rep_data_list["Test0"]["query"],
                                      self.vt_rep_data_list["Test1"]["query"]])

        self.assertEqual(2, len(actual))
        self.assertGreaterEqual(15, (start - datetime.datetime.now()).total_seconds())
        self.assertDictEqual(self.vt_rep_data_list["Test0"]["expected"], actual[0])
        self.assertDictEqual(self.vt_rep_data_list["Test1"]["expected"], actual[1])

    @patch("libchickadee.resolvers.virustotal.requests.get")
    def test_resolve_errors(self, mock_requests):
        subtests = {
            400: "Incorrect request. Please check input data",
            403: "Authorization error. Please check API key",
            500: "Unknown error occurred, status code 500, please report"
        }
        for status_code, err_msg in subtests.items():
            mock_requests.return_value.status_code = status_code
            with self.subTest(id=status_code):
                with self.assertLogs('libchickadee.resolvers.virustotal', level='ERROR') as mock_log:
                    actual = self.resolver.query(self.vt_rep_data_list["Test0"]["query"])
                self.assertIsNone(actual)
                self.assertEqual(mock_log.records[0].message, err_msg)

    @patch("libchickadee.resolvers.virustotal.requests.get")
    def test_sleeper(self, mock_requests):
        initial_time = datetime.datetime.now()
        self.resolver.last_request = initial_time
        time.sleep(2)
        mock_requests.return_value.status_code = 403

        self.resolver.query(data='1.1.1.1')
        self.assertGreaterEqual(self.resolver.last_request, initial_time + datetime.timedelta(seconds=2))


if __name__ == "__main__":
    unittest.main()
