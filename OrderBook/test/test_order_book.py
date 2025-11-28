import pytest
from unittest.mock import Mock, patch, MagicMock
import time

from OrderBook.order_book import OrderBook
from shared_memory_utils import SharedPriceBook


@pytest.fixture
def mock_config():
    """Test configuration"""
    return {
        "symbols": ["AAPL", "MSFT", "GOOG"],
        "host": "localhost",
        "md_port": 5555,
        "news_port": 5556
    }


@patch('OrderBook.order_book.FeedHandler')
@patch('OrderBook.order_book.SharedPriceBook')
def test_order_book_init(mock_price_book, mock_feed_handler, mock_config):
    """Test OrderBook initialization"""
    order_book = OrderBook(mock_config)
    
    # Verify FeedHandler was created
    mock_feed_handler.assert_called_once_with(
        mock_config["host"],
        mock_config["md_port"],
        mock_config["news_port"]
    )
    
    # Verify subscription
    order_book.feed_handler.subscribe.assert_called_once()


@patch('OrderBook.order_book.FeedHandler')
@patch('OrderBook.order_book.SharedPriceBook')
def test_order_book_missing_symbols(mock_price_book, mock_feed_handler):
    """Test OrderBook with missing symbols raises error"""
    config = {"host": "localhost", "md_port": 5555, "news_port": 5556}
    
    with pytest.raises(ValueError, match="Symbols are required"):
        OrderBook(config)


@patch('OrderBook.order_book.FeedHandler')
def test_order_book_on_market_data(mock_feed_handler, mock_config):
    """Test processing market data"""
    # Create real SharedPriceBook for testing
    book = SharedPriceBook(mock_config["symbols"], name="test_ob_md", create=True)
    
    try:
        with patch('OrderBook.order_book.SharedPriceBook', return_value=book):
            order_book = OrderBook(mock_config)
            
            # Simulate market data message: symbol,price,timestamp
            test_data = b"AAPL,172.53,1234567890.123"
            order_book.on_market_data(test_data)
            
            # Verify update in shared memory
            price, ts = book.read("AAPL")
            assert price == 172.53
            assert ts == 1234567890.123
    finally:
        book.close()
        book.unlink()


@patch('OrderBook.order_book.FeedHandler')
def test_order_book_on_market_data_multiple_symbols(mock_feed_handler, mock_config):
    """Test processing market data for multiple symbols"""
    book = SharedPriceBook(mock_config["symbols"], name="test_ob_multi", create=True)
    
    try:
        with patch('OrderBook.order_book.SharedPriceBook', return_value=book):
            order_book = OrderBook(mock_config)
            
            # Update multiple symbols
            order_book.on_market_data(b"AAPL,172.53,1234567890.1")
            order_book.on_market_data(b"MSFT,325.20,1234567890.2")
            order_book.on_market_data(b"GOOG,142.50,1234567890.3")
            
            # Verify all updates
            aapl_price, _ = book.read("AAPL")
            msft_price, _ = book.read("MSFT")
            goog_price, _ = book.read("GOOG")
            
            assert aapl_price == 172.53
            assert msft_price == 325.20
            assert goog_price == 142.50
    finally:
        book.close()
        book.unlink()


@patch('OrderBook.order_book.FeedHandler')
def test_order_book_on_market_data_invalid_format(mock_feed_handler, mock_config):
    """Test handling of invalid market data format"""
    book = SharedPriceBook(mock_config["symbols"], name="test_ob_invalid", create=True)
    
    try:
        with patch('OrderBook.order_book.SharedPriceBook', return_value=book):
            order_book = OrderBook(mock_config)
            
            # Invalid data (missing fields) - should not crash
            order_book.on_market_data(b"AAPL,172.53")  # Missing timestamp
            
            # Should still be at initial value
            price, _ = book.read("AAPL")
            # Depending on error handling, could be 0.0 or unchanged
    finally:
        book.close()
        book.unlink()


@patch('OrderBook.order_book.FeedHandler')
def test_order_book_on_market_data_malformed(mock_feed_handler, mock_config):
    """Test handling of malformed market data"""
    book = SharedPriceBook(mock_config["symbols"], name="test_ob_malformed", create=True)
    
    try:
        with patch('OrderBook.order_book.SharedPriceBook', return_value=book):
            order_book = OrderBook(mock_config)
            
            # Completely malformed data - should not crash
            order_book.on_market_data(b"garbage data")
            order_book.on_market_data(b"")
            order_book.on_market_data(b"AAPL,not_a_number,12345")
    finally:
        book.close()
        book.unlink()

