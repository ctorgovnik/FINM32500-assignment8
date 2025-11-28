# Examples

Simple usage examples for the trading system components.

## OrderManager Example

**`order_manager_example.py`** - Demonstrates starting the OrderManager server and sending orders using the client library.

### Usage

```bash
python examples/order_manager_example.py
```

This example:
1. Starts an OrderManager server in the background
2. Connects a client to the server
3. Sends three sample orders (BUY/SELL)
4. Disconnects gracefully

### What You'll See

```
OrderManager Usage Example

Starting OrderManager server...
Connecting client...

Sending orders:
  Sent: BUY 100 AAPL @ $172.53
  Sent: SELL 50 MSFT @ $325.20
  Sent: BUY 25 GOOG @ $142.50

Done
```

The server logs will show the orders being received and executed.

## Integration with Strategy

In your trading system, the Strategy process will use the client similarly:

```python
from OrderManager.client import OrderManagerClient

class Strategy:
    def __init__(self, config):
        self.order_client = OrderManagerClient(
            host=config["order_manager_host"],
            port=config["order_manager_port"]
        )
        self.order_client.connect()
    
    def on_signal(self, symbol, side, quantity, price):
        self.order_client.place_order(symbol, side, quantity, price)
```
