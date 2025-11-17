import pytest
from serializers import MessageSerializer

def test_serialize_price():
    serializer = MessageSerializer()
    result = serializer.serialize_price("AAPL", "172.53")
    assert result == b"AAPL,172.53"

def test_serialize_sentiment():
    serializer = MessageSerializer()
    result = serializer.serialize_sentiment(75)
    assert result == b"75"

def test_add_delimiter():
    serializer = MessageSerializer()
    result = serializer.add_delimiter(b"test")
    assert result == b"test*"

def test_serialize_price_with_delimiter():
    serializer = MessageSerializer()
    result = serializer.serialize_price_with_delimiter("MSFT", "325.20")
    assert result == b"MSFT,325.20*"

