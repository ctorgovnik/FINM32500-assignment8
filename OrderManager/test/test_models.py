import pytest
import time
from OrderManager.models import Order, Side


def test_side_values():
    """Test Side enum values"""
    assert Side.BUY.value == "BUY"
    assert Side.SELL.value == "SELL"

def test_side_from_string():
    """Test creating Side from string"""
    assert Side("BUY") == Side.BUY
    assert Side("SELL") == Side.SELL

def test_side_string_representation():
    """Test Side string representation"""
    assert str(Side.BUY) == "BUY"
    assert str(Side.SELL) == "SELL"

def test_order_creation():
    """Test creating a valid order"""
    order = Order(
        symbol="AAPL",
        quantity=100,
        price=150.50,
        side=Side.BUY
    )
    
    assert order.symbol == "AAPL"
    assert order.quantity == 100
    assert order.price == 150.50
    assert order.side == Side.BUY
    assert order.timestamp is not None

def test_order_with_timestamp():
    """Test order with explicit timestamp"""
    ts = time.time()
    order = Order(
        symbol="MSFT",
        quantity=50,
        price=300.00,
        side=Side.SELL,
        timestamp=ts
    )
    
    assert order.timestamp == ts

def test_order_side_from_string():
    """Test order accepts side as string"""
    order = Order(
        symbol="GOOG",
        quantity=25,
        price=140.00,
        side="BUY"
    )
    
    assert order.side == Side.BUY
    assert isinstance(order.side, Side)

def test_order_validation_negative_quantity():
    """Test negative quantity raises error"""
    with pytest.raises(ValueError, match="Quantity must be positive"):
        Order(
            symbol="AAPL",
            quantity=-10,
            price=150.00,
            side=Side.BUY
        )

def test_order_validation_zero_quantity():
    """Test zero quantity raises error"""
    with pytest.raises(ValueError, match="Quantity must be positive"):
        Order(
            symbol="AAPL",
            quantity=0,
            price=150.00,
            side=Side.BUY
        )

def test_order_validation_negative_price():
    """Test negative price raises error"""
    with pytest.raises(ValueError, match="Price must be positive"):
        Order(
            symbol="AAPL",
            quantity=10,
            price=-150.00,
            side=Side.BUY
        )

def test_order_validation_zero_price():
    """Test zero price raises error"""
    with pytest.raises(ValueError, match="Price must be positive"):
        Order(
            symbol="AAPL",
            quantity=10,
            price=0.0,
            side=Side.BUY
        )

def test_order_validation_empty_symbol():
    """Test empty symbol raises error"""
    with pytest.raises(ValueError, match="Symbol cannot be empty"):
        Order(
            symbol="",
            quantity=10,
            price=150.00,
            side=Side.BUY
        )

def test_order_to_bytes():
    """Test order serialization to bytes"""
    order = Order(
        symbol="AAPL",
        quantity=100,
        price=150.50,
        side=Side.BUY,
        timestamp=1234567890.123
    )
    
    result = order.to_bytes()
    
    assert isinstance(result, bytes)
    assert result.endswith(b'*')
    assert b'AAPL' in result
    assert b'100' in result
    assert b'150.5' in result
    assert b'BUY' in result
    assert b'1234567890.123' in result

def test_order_from_bytes():
    """Test order deserialization from bytes"""
    data = b'1234567890.123,BUY,100,AAPL,150.5*'
    order = Order.from_bytes(data)
    
    assert order.symbol == "AAPL"
    assert order.quantity == 100
    assert order.price == 150.5
    assert order.side == Side.BUY
    assert order.timestamp == 1234567890.123

def test_order_roundtrip():
    """Test order serialization roundtrip"""
    original = Order(
        symbol="MSFT",
        quantity=50,
        price=325.75,
        side=Side.SELL,
        timestamp=1234567890.5
    )
    
    serialized = original.to_bytes()
    deserialized = Order.from_bytes(serialized)
    
    assert deserialized.symbol == original.symbol
    assert deserialized.quantity == original.quantity
    assert deserialized.price == original.price
    assert deserialized.side == original.side
    assert deserialized.timestamp == original.timestamp

def test_order_from_bytes_invalid_format():
    """Test invalid format raises error"""
    with pytest.raises(ValueError, match="Invalid order data"):
        Order.from_bytes(b'invalid,data*')

def test_order_from_bytes_invalid_side():
    """Test invalid side raises error"""
    with pytest.raises(ValueError):
        Order.from_bytes(b'1234567890.123,INVALID,100,AAPL,150.5*')

def test_order_str_representation():
    """Test order string representation"""
    order = Order(
        symbol="AAPL",
        quantity=100,
        price=150.50,
        side=Side.BUY,
        timestamp=1234567890.123
    )
    
    result = str(order)
    assert "BUY" in result
    assert "100" in result
    assert "AAPL" in result
    assert "150.50" in result

def test_order_repr():
    """Test order repr"""
    order = Order(
        symbol="AAPL",
        quantity=100,
        price=150.50,
        side=Side.BUY,
        timestamp=1234567890.123
    )
    
    result = repr(order)
    assert "Order(" in result
    assert "symbol='AAPL'" in result
    assert "side=BUY" in result

