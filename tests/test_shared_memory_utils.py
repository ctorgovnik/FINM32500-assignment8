import unittest
import pytest
from shared_memory_utils import SharedPriceBook

class TestSharedMemoryUtils(unittest.TestCase):
    def test_shared_memory_size_zero(self):
        with pytest.raises(ValueError):
            SharedPriceBook(symbols = [])

    def test_shared_memory_size_one(self):
        shared_price_book = SharedPriceBook(symbols = ["APPL"])
        assert 56 == shared_price_book.shared_memory_size()
        shared_price_book.close()

    def test_shared_memory_size_two(self):
        shared_price_book = SharedPriceBook(symbols = ["APPL", "MSFT"])
        assert 112 == shared_price_book.shared_memory_size()
        shared_price_book.close()

    def test_shared_memory_size_five(self):
        shared_price_book = SharedPriceBook(symbols = ["APPL", "MSFT", "ABC", "DEF", "GHI"])
        assert 280 == shared_price_book.shared_memory_size()
        shared_price_book.close()