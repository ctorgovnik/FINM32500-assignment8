from dataclasses import dataclass
from datetime import datetime
from enum import Enum


@dataclass(frozen=True)
class MarketDataPoint:
    """Frozen dataclass representing a market data point."""

    timestamp: datetime
    symbol: str
    price: float

class OrderStatus(str, Enum):
    """Enum representing the status of an order.
    
    Lifecycle:
    - PENDING: Submitted, waiting for exchange acknowledgment
    - ACTIVE: On exchange, can be filled
    - PARTIALLY_FILLED: Partially filled, still active
    - FILLED: Fully filled (terminal)
    - CANCELED: Canceled (terminal)
    - FAILED: Failed to submit (terminal)
    """

    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    FAILED = "FAILED"

class Order:
    """Mutable class representing a trade order."""

    def __init__(self, symbol: str, quantity: int, price: float, status: OrderStatus, id: str | None = None, filled_quantity: int = 0):
        self.symbol = symbol
        self.quantity = quantity  # Total order quantity
        self.price = price
        self.status = status
        self.id = id
        
        self.filled_quantity = filled_quantity  # How much has been filled so far
        
    @property
    def remaining_quantity(self) -> int:
        """Get remaining quantity to fill."""
        return abs(self.quantity) - self.filled_quantity
    
    @property
    def is_fully_filled(self) -> bool:
        """Check if order is fully filled."""
        return self.filled_quantity >= abs(self.quantity)

class Action(str, Enum):
    """Enum representing the action of an order."""

    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class RecordingInterval(str, Enum):
    """Enum representing the frequency of portfolio value recording."""
    
    TICK = "tick"           # Every tick
    SECOND = "1s"           # Every 1 second
    MINUTE = "1m"           # Every 1 minute
    HOURLY = "1h"           # Every hour
    DAILY = "1d"            # Once per day
    WEEKLY = "1w"           # Once per week
    MONTHLY = "1mo"         # Once per month
