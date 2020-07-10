"""EVTX parsing tests."""
import unittest
import os

from libchickadee.parsers.evtx import EVTXParser

__author__ = 'Chapin Bryce'
__date__ = 20200710
__license__ = 'MIT Copyright 2020 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''


class EVTXParserTestCase(unittest.TestCase):
    """EVTX parsing tests."""
    def setUp(self):
        """Test Config."""
        self.test_data_ips = {
            "39.194.200.3": 4,
            "37.189.201.3": 2,
            "39.195.200.3": 2,
            "216.93.146.189": 166,
            "32.0.0.156": 198,
            "32.0.0.114": 10,
            "18.8.8.0": 4
        }
        self.parser = EVTXParser(ignore_bogon=False)
        self.test_data_dir = os.path.join(
            os.path.dirname(__file__), 'test_data')

    def test_ip_extraction_evtx(self):
        """Extraction test."""
        self.parser.parse_file(os.path.join(self.test_data_dir, 'test_ips.evtx'))
        self.assertEqual(self.test_data_ips, self.parser.ips)


if __name__ == '__main__':
    unittest.main()
