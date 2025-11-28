from dataclasses import dataclass
from enum import Enum
import time
from typing import Optional

class Side(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    
    def __str__(self):
        return self.value

@dataclass
class Order:
    symbol: str
    quantity: int
    price: float
    side: Side
    timestamp: float = None
    order_id: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if isinstance(self.side, str):
            self.side = Side(self.side.upper())
        
        # Basic validation
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.price <= 0:
            raise ValueError("Price must be positive")
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")

    @classmethod
    def from_bytes(cls, data: bytes, field_delim: str = ',', msg_delim: bytes = b'*') -> 'Order':
        try:
            text = data.rstrip(msg_delim).decode('utf-8')
            parts = text.split(field_delim)
            
            if len(parts) != 5:
                raise ValueError(f"Expected 5 fields, got {len(parts)}")
            
            timestamp, side, quantity, symbol, price = parts
            
            return cls(
                symbol=symbol,
                quantity=int(quantity),
                price=float(price),
                side=Side(side),
                timestamp=float(timestamp)
            )
        except (ValueError, KeyError) as e:
            raise ValueError(
                f"Invalid order data: {data.decode('utf-8', errors='replace')}. "
                f"Expected format: timestamp,side,quantity,symbol,price*"
            ) from e
    
    def to_bytes(self, field_delim: str = ',', msg_delim: bytes = b'*') -> bytes:
        order_str = field_delim.join([
            str(self.timestamp),
            self.side.value,
            str(self.quantity),
            self.symbol,
            str(self.price)
        ])
        return order_str.encode('utf-8') + msg_delim
    
    def __str__(self):
        return f"[{self.timestamp}] {self.side} {self.quantity} {self.symbol} @ {self.price:.2f}"
    
    def __repr__(self):
        return (
            f"Order(symbol='{self.symbol}', side={self.side.value}, "
            f"quantity={self.quantity}, price={self.price:.2f}, "
            f"timestamp={self.timestamp})"
        )

