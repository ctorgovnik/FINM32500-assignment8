from enum import Enum
from dataclasses import dataclass

class Side(str, Enum):
    """Enum representing the side of an order."""

    BUY = "BUY"
    SELL = "SELL"

@dataclass
class Order:
    symbol: str
    quantity: int
    price: float
    side: Side
    timestamp: float

    def __str__(self):
        return f"[{self.timestamp}] {self.side} {self.quantity} {self.symbol} @ {self.price}"
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'Order':
        try:
            text = data.rstrip(b'*').decode('utf-8')
            timestamp, side, quantity, symbol, price = text.split(',')
            return cls(symbol, int(quantity), float(price), Side(side), float(timestamp))
        except Exception as e:
            raise ValueError(f"Invalid order data: {data}: {e}")
    
    def to_bytes(self) -> bytes:
        return f"{self.timestamp},{self.side.value},{self.quantity},{self.symbol},{self.price}".encode('utf-8') + b'*'