import unittest

from libchickadee.test import test_backend_ipapi
from libchickadee.test import test_parser_xlsx
from libchickadee.test import test_parser_plaintext
from libchickadee.test import test_chickadee

loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(loader.loadTestsFromModule(test_backend_ipapi))
suite.addTests(loader.loadTestsFromModule(test_parser_xlsx))
suite.addTests(loader.loadTestsFromModule(test_parser_plaintext))
suite.addTests(loader.loadTestsFromModule(test_chickadee))

runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
