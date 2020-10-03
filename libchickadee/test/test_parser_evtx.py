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
        self.test_data_ips = {'127.0.0.1': 6}
        self.parser = EVTXParser(ignore_bogon=False)
        self.test_data_dir = os.path.join(
            os.path.dirname(__file__), 'test_data')

    def test_ip_extraction_evtx(self):
        """Extraction test."""
        self.parser.parse_file(os.path.join(self.test_data_dir, 'System2.evtx'))
        self.assertEqual(self.test_data_ips, self.parser.ips)


if __name__ == '__main__':
    unittest.main()
