import pytest
import socket
import threading
import time
from OrderManager.client import OrderManagerClient
from OrderManager.models import Order, Side


class MockServer:
    """Mock server for testing client"""
    
    def __init__(self, port):
        self.port = port
        self.server_socket = None
        self.received_data = []
        self.running = False
        self.thread = None
    
    def start(self):
        """Start mock server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('localhost', self.port))
        self.server_socket.listen(1)
        self.running = True
        
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        time.sleep(0.1)  # Give server time to start
    
    def _run(self):
        """Server main loop"""
        try:
            self.server_socket.settimeout(1.0)
            while self.running:
                try:
                    client_socket, _ = self.server_socket.accept()
                    data = client_socket.recv(1024)
                    if data:
                        self.received_data.append(data)
                    client_socket.close()
                except socket.timeout:
                    continue
        except Exception:
            pass
    
    def stop(self):
        """Stop mock server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        if self.thread:
            self.thread.join(timeout=2.0)


def test_client_creation():
    """Test creating client"""
    client = OrderManagerClient('localhost', 9000)
    assert client.host == 'localhost'
    assert client.port == 9000
    assert not client.connected

def test_client_connect():
    """Test client connection"""
    server = MockServer(9201)
    server.start()
    
    try:
        client = OrderManagerClient('localhost', 9201)
        result = client.connect()
        
        assert result is True
        assert client.connected is True
        
        client.disconnect()
    finally:
        server.stop()

def test_client_connect_failure():
    """Test client connection failure"""
    client = OrderManagerClient('localhost', 9299)  # No server listening
    result = client.connect()
    assert result is False

def test_client_send_order():
    """Test sending order to server"""
    server = MockServer(9202)
    server.start()
    
    try:
        client = OrderManagerClient('localhost', 9202)
        client.connect()
        
        order = Order(
            symbol="AAPL",
            quantity=100,
            price=150.50,
            side=Side.BUY
        )
        
        result = client.send_order(order)
        assert result is True
        
        time.sleep(0.1)
        
        assert len(server.received_data) == 1
        received = server.received_data[0]
        assert b'AAPL' in received
        assert b'100' in received
        assert b'BUY' in received
        
        client.disconnect()
    finally:
        server.stop()

def test_client_place_order():
    """Test place_order convenience method"""
    server = MockServer(9203)
    server.start()
    
    try:
        client = OrderManagerClient('localhost', 9203)
        client.connect()
        
        result = client.place_order("MSFT", "SELL", 50, 325.00)
        assert result is True
        
        time.sleep(0.1)
        
        assert len(server.received_data) == 1
        received = server.received_data[0]
        assert b'MSFT' in received
        assert b'50' in received
        assert b'SELL' in received
        
        client.disconnect()
    finally:
        server.stop()

def test_client_send_without_connect():
    """Test sending order without connection"""
    client = OrderManagerClient('localhost', 9000)
    
    order = Order(
        symbol="AAPL",
        quantity=100,
        price=150.50,
        side=Side.BUY
    )
    
    result = client.send_order(order)
    assert result is False

def test_client_disconnect():
    """Test client disconnect"""
    server = MockServer(9205)
    server.start()
    
    try:
        client = OrderManagerClient('localhost', 9205)
        client.connect()
        assert client.connected is True
        
        client.disconnect()
        assert client.connected is False
        assert client.socket is None
    finally:
        server.stop()
