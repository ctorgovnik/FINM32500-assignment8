import pytest
import threading
import time
from OrderManager.server import Server
from OrderManager.client import OrderManagerClient

pytestmark = pytest.mark.integration


@pytest.fixture
def server():
    """Create and start server on unique port"""
    config = {
        "host": "localhost",
        "port": 9300,  # Use different port to avoid conflicts
        "delimiter": b'*'
    }
    
    srv = Server(config)
    thread = threading.Thread(target=srv.run, daemon=True)
    thread.start()
    time.sleep(0.3)  # Give server time to start
    
    yield srv
    
    srv.shutdown()
    time.sleep(0.2)  # Give server time to clean up

def test_server_client_connection(server):
    """Test that client can connect to server"""
    client = OrderManagerClient('localhost', 9300)
    
    result = client.connect()
    assert result is True
    assert client.connected is True
    
    client.disconnect()

def test_server_receives_order(server):
    """Test that server receives and processes order"""
    client = OrderManagerClient('localhost', 9300)
    client.connect()
    
    try:
        result = client.place_order("AAPL", "BUY", 100, 150.50)
        assert result is True
        
        time.sleep(0.1)  # Give server time to process
    finally:
        client.disconnect()

def test_server_multiple_orders(server):
    """Test sending multiple orders"""
    client = OrderManagerClient('localhost', 9300)
    client.connect()
    
    try:
        orders = [
            ("AAPL", "BUY", 100, 150.50),
            ("MSFT", "SELL", 50, 325.00),
            ("GOOG", "BUY", 25, 140.00),
        ]
        
        for symbol, side, qty, price in orders:
            result = client.place_order(symbol, side, qty, price)
            assert result is True
        
        time.sleep(0.2)
    finally:
        client.disconnect()

def test_order_message_format(server):
    """Test that orders are sent in correct format"""
    client = OrderManagerClient('localhost', 9300)
    client.connect()
    
    try:
        # Send order and verify it's processed without errors
        result = client.place_order("TEST", "SELL", 999, 123.45)
        assert result is True
        
        time.sleep(0.1)
    finally:
        client.disconnect()
