import pytest
import unittest

class test_system(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        print("setup_class()")
    @classmethod
    def teardown_class(cls):
        print("teardown_class()")
    def test_search_all(self):
        assert True
