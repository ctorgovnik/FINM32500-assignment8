import pytest
import socket
from unittest.mock import Mock, MagicMock
from stream import Stream

def test_stream_broadcast_single_client(mock_provider):
    stream = Stream(mock_provider, 0, delimiter=b'*')
    
    mock_socket = MagicMock()
    mock_socket.sendall = Mock()
    
    stream.clients.append(mock_socket)
    
    stream.broadcast(b"message")
    assert len(stream.clients) == 1
    mock_socket.sendall.assert_called_once()

def test_stream_adds_delimiter(mock_provider):
    stream = Stream(mock_provider, 0, delimiter=b'*')
    
    received = []
    mock_socket = MagicMock()
    mock_socket.sendall = Mock(side_effect=lambda data: received.append(data))
    
    stream.clients.append(mock_socket)
    stream.broadcast(b"message")
    
    assert received[0] == b"message*"

def test_stream_removes_dead_clients(mock_provider):
    stream = Stream(mock_provider, 0)
    
    good_socket = MagicMock()
    good_socket.sendall = Mock()
    
    bad_socket = MagicMock()
    bad_socket.sendall = Mock(side_effect=ConnectionError("Dead socket"))
    
    stream.clients = [good_socket, bad_socket]
    
    stream.broadcast(b"test")
    
    assert len(stream.clients) == 1
    assert good_socket in stream.clients
    assert bad_socket not in stream.clients

