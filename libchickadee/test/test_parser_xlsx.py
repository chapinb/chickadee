"""XLSX parsing tests."""
import unittest
import os

from libchickadee.parsers.xlsx import XLSXParser

__author__ = 'Chapin Bryce'
__date__ = 20200107
__license__ = 'MIT Copyright 2020 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''


class XLSXParserTestCase(unittest.TestCase):
    """XLSX parsing tests."""
    def setUp(self):
        """Test Config."""
        self.test_data_ips = {
            '10.0.1.2': 1,
            '8.8.8.8': 1,
            '1.1.1.1': 2,
            '2.2.2.2': 1,
            '4.4.4.4': 1,
            '2001:4860:4860::8844': 2,
            '2001:4860:4860::8888': 1
        }
        self.parser = XLSXParser(ignore_bogon=False)
        self.test_data_dir = os.path.join(
            os.path.dirname(__file__), 'test_data')

    def test_ip_extraction_xlsx(self):
        """Extraction test."""
        self.parser.parse_file(os.path.join(self.test_data_dir, 'test_ips.xlsx'))
        self.assertEqual(self.test_data_ips, self.parser.ips)


if __name__ == '__main__':
    unittest.main()
