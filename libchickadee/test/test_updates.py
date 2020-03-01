"""Plain-text parsing tests"""
import unittest

from libchickadee import __version__
from libchickadee.update import update_available, get_pypi_version

__author__ = 'Chapin Bryce'
__date__ = 20200229
__license__ = 'MIT Copyright 2020 Chapin Bryce'
__desc__ = '''Yet another GeoIP resolution tool.'''


class TestUpdate(unittest.TestCase):
    def test_up_to_date(self):
        """Test version up to date"""
        last_public_release = get_pypi_version()
        self.assertFalse(update_available(last_public_release))

    def test_out_of_date(self):
        """Test version out of date"""
        self.assertTrue(update_available(0.0))

    def test_get_pypi_version(self):
        """Test pypi version type"""
        pypi_version = get_pypi_version()
        self.assertIsInstance(pypi_version, float)

    def test_local_version(self):
        """Test pypi version type"""
        self.assertIsInstance(__version__, float)


if __name__ == '__main__':
    unittest.main()
