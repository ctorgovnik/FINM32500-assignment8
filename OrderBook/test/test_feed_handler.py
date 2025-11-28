import pytest
import socket
import threading
import time
from unittest.mock import Mock, MagicMock, patch

from OrderBook.feed_handler import FeedHandler


@pytest.fixture
def mock_server():
    """Create a mock server for testing"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('localhost', 0))  # Bind to any available port
    server_socket.listen(2)
    
    port = server_socket.getsockname()[1]
    
    def accept_connections():
        clients = []
        for _ in range(2):  # Accept 2 connections (md and news)
            client, addr = server_socket.accept()
            clients.append(client)
        return clients
    
    yield server_socket, port, accept_connections
    
    server_socket.close()


def test_feed_handler_subscribe():
    """Test subscribing to feeds"""
    with patch('socket.socket'):
        handler = FeedHandler("localhost", 5555, 5556)
        
        callback = Mock()
        handler.subscribe(callback, "market_data")
        
        assert len(handler.subscribers["market_data"]) == 1
        assert callback in handler.subscribers["market_data"]


def test_feed_handler_subscribe_invalid_feed():
    """Test subscribing to invalid feed type"""
    with patch('socket.socket'):
        handler = FeedHandler("localhost", 5555, 5556)
        
        callback = Mock()
        with pytest.raises(ValueError):
            handler.subscribe(callback, "invalid_feed_type")


def test_feed_handler_socket_mapping():
    """Test that sockets are properly mapped to feed types"""
    with patch('socket.socket') as mock_socket:
        # Create mock socket instances
        md_socket = MagicMock()
        news_socket = MagicMock()
        
        mock_socket.side_effect = [md_socket, news_socket]
        
        handler = FeedHandler("localhost", 5555, 5556)
        
        assert handler.socket_to_feed_type[md_socket] == "market_data"
        assert handler.socket_to_feed_type[news_socket] == "news"


def test_feed_handler_listen_calls_subscribers(mock_server):
    """Test that listen() calls subscribers with received data"""
    server_socket, port, accept_connections = mock_server
    
    # Start server thread
    clients = []
    def server_thread():
        nonlocal clients
        clients = accept_connections()
        # Send test data
        clients[0].sendall(b"AAPL,172.53*")
        clients[0].close()
        clients[1].close()
    
    server = threading.Thread(target=server_thread, daemon=True)
    server.start()
    
    # Create handler (will connect to mock server)
    handler = FeedHandler("localhost", port, port)
    
    # Subscribe to market data
    received_data = []
    def callback(data):
        received_data.append(data)
    
    handler.subscribe(callback, "market_data")
    
    # Start listening in a thread
    listen_thread = threading.Thread(
        target=handler.listen, 
        args=(handler.md_client_socket,),
        daemon=True
    )
    listen_thread.start()
    
    # Wait for data
    time.sleep(0.2)
    
    # Check that callback was called
    assert len(received_data) > 0
    assert b"AAPL" in received_data[0]


def test_feed_handler_multiple_subscribers():
    """Test multiple subscribers to same feed"""
    with patch('socket.socket'):
        handler = FeedHandler("localhost", 5555, 5556)
        
        callback1 = Mock()
        callback2 = Mock()
        
        handler.subscribe(callback1, "market_data")
        handler.subscribe(callback2, "market_data")
        
        assert len(handler.subscribers["market_data"]) == 2


def test_feed_handler_separate_feeds():
    """Test that market_data and news feeds are separate"""
    with patch('socket.socket'):
        handler = FeedHandler("localhost", 5555, 5556)
        
        md_callback = Mock()
        news_callback = Mock()
        
        handler.subscribe(md_callback, "market_data")
        handler.subscribe(news_callback, "news")
        
        assert md_callback in handler.subscribers["market_data"]
        assert news_callback in handler.subscribers["news"]
        assert md_callback not in handler.subscribers["news"]
        assert news_callback not in handler.subscribers["market_data"]

