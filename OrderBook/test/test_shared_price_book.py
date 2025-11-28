import pytest
import time
import multiprocessing as mp
from multiprocessing import Process

from shared_memory_utils import SharedPriceBook


def test_shared_price_book_create():
    """Test creating a shared price book"""
    symbols = ["AAPL", "MSFT", "GOOG"]
    book = SharedPriceBook(symbols, name="test_create", create=True)
    
    try:
        # Verify initialization
        assert book.num_symbols == 3
        assert len(book.symbol_index) == 3
        assert "AAPL" in book.symbol_index
        
        # Verify initial prices are 0
        price, ts = book.read("AAPL")
        assert price == 0.0
        assert ts == 0.0
    finally:
        book.close()
        book.unlink()


def test_shared_price_book_update_and_read():
    """Test updating and reading prices"""
    symbols = ["AAPL", "MSFT"]
    book = SharedPriceBook(symbols, name="test_update", create=True)
    
    try:
        # Update price
        book.update("AAPL", 172.53, time.time())
        
        # Read back
        price, ts = book.read("AAPL")
        assert price == 172.53
        assert ts > 0
        
        # Update another symbol
        book.update("MSFT", 325.20, time.time())
        price, ts = book.read("MSFT")
        assert price == 325.20
    finally:
        book.close()
        book.unlink()


def test_shared_price_book_invalid_symbol():
    """Test reading/updating invalid symbol"""
    symbols = ["AAPL"]
    book = SharedPriceBook(symbols, name="test_invalid", create=True)
    
    try:
        # Try to update invalid symbol (should log error but not crash)
        book.update("INVALID", 100.0, time.time())
        
        # Try to read invalid symbol
        price, ts = book.read("INVALID")
        assert price is None
        assert ts is None
    finally:
        book.close()
        book.unlink()


def test_shared_price_book_multiple_updates():
    """Test multiple updates to same symbol"""
    symbols = ["AAPL"]
    book = SharedPriceBook(symbols, name="test_multi", create=True)
    
    try:
        t1 = time.time()
        book.update("AAPL", 170.0, t1)
        
        time.sleep(0.01)
        
        t2 = time.time()
        book.update("AAPL", 172.0, t2)
        
        price, ts = book.read("AAPL")
        assert price == 172.0
        assert ts == t2
        assert ts > t1
    finally:
        book.close()
        book.unlink()


def writer_process(symbols, name):
    """Helper function for multiprocess test - writes prices"""
    book = SharedPriceBook(symbols, name=name, create=False)
    try:
        for i in range(5):
            book.update("AAPL", 170.0 + i, time.time())
            time.sleep(0.05)
    finally:
        book.close()


def reader_process(symbols, name, results_queue):
    """Helper function for multiprocess test - reads prices"""
    book = SharedPriceBook(symbols, name=name, create=False)
    try:
        prices_seen = []
        for _ in range(5):
            price, ts = book.read("AAPL")
            if price is not None:
                prices_seen.append(price)
            time.sleep(0.05)
        results_queue.put(prices_seen)
    finally:
        book.close()


def test_shared_price_book_multiprocess():
    """Test shared memory across multiple processes"""
    symbols = ["AAPL", "MSFT"]
    name = "test_multiproc"
    
    # Create shared memory in main process
    book = SharedPriceBook(symbols, name=name, create=True)
    
    try:
        # Start writer process
        writer = Process(target=writer_process, args=(symbols, name))
        writer.start()
        
        # Start reader process
        results_queue = mp.Queue()
        reader = Process(target=reader_process, args=(symbols, name, results_queue))
        reader.start()
        
        # Wait for completion
        writer.join(timeout=2)
        reader.join(timeout=2)
        
        # Check results
        prices_seen = results_queue.get(timeout=1)
        assert len(prices_seen) > 0
        # Should see increasing prices
        assert max(prices_seen) >= 170.0
        
    finally:
        book.close()
        book.unlink()


def test_shared_price_book_attach():
    """Test attaching to existing shared memory"""
    symbols = ["AAPL"]
    name = "test_attach"
    
    # Create in one instance
    book1 = SharedPriceBook(symbols, name=name, create=True)
    book1.update("AAPL", 175.0, time.time())
    
    try:
        # Attach in another instance
        book2 = SharedPriceBook(symbols, name=name, create=False)
        
        try:
            # Should see the same data
            price, ts = book2.read("AAPL")
            assert price == 175.0
            
            # Update from book2
            book2.update("AAPL", 180.0, time.time())
            
            # Read from book1
            price, ts = book1.read("AAPL")
            assert price == 180.0
        finally:
            book2.close()
    finally:
        book1.close()
        book1.unlink()


def test_shared_price_book_close_twice():
    """Test that closing twice doesn't crash"""
    symbols = ["AAPL"]
    book = SharedPriceBook(symbols, name="test_close_twice", create=True)
    
    try:
        book.close()
        book.close()  # Should not crash
    finally:
        # Unlink still works after close
        book.unlink()

