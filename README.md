# Trading System - Interprocess Communication

A multi-process trading system using TCP sockets and shared memory for interprocess communication.

## System Architecture

```
┌─────────────┐       ┌──────────────┐       ┌────────────┐       ┌───────────────┐
│   Gateway   │──────▶│  OrderBook   │──────▶│  Strategy  │──────▶│ OrderManager  │
│             │ TCP   │              │ Shared│            │ TCP   │               │
│ Market Data │       │Shared Memory │Memory │  Signals   │       │    Orders     │
│  & News     │       │ Price Book   │       │            │       │               │
└─────────────┘       └──────────────┘       └────────────┘       └───────────────┘
```

## Components

### 1. Gateway (`Gateway/`)
**Status:** ✅ Complete

Streams market data and news sentiment over TCP sockets.

- **Market Data Stream** (port 8000): Real-time price updates
- **News Stream** (port 8001): Sentiment values (0-100)
- Format: `SYMBOL,PRICE*` with `*` delimiter

### 2. OrderBook (`OrderBook/`)
**Status:** ✅ Complete

Receives price data and maintains shared memory.

- Subscribes to Gateway market data feed
- Updates `SharedPriceBook` in shared memory
- Provides atomic, lock-protected price updates

### 3. Strategy (`Strategy/`)
**Status:** ⚠️ Placeholder

Generates trading signals (TO BE IMPLEMENTED).

Requirements:
- Read prices from shared memory
- Subscribe to news feed
- Implement moving average crossover
- Implement news-based signals
- Send orders to OrderManager

### 4. OrderManager (`OrderManager/`)
**Status:** ✅ Complete

TCP server that receives and logs orders.

- Listens on port 9000
- Deserializes orders
- Logs executed trades
- Handles multiple strategy clients

### 5. Shared Memory (`shared_memory_utils.py`)
**Status:** ✅ Complete

Thread-safe shared memory for prices using NumPy arrays.

- Lock-protected updates
- Efficient zero-copy reads/writes
- Process-safe

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the System

```bash
python main.py
```

This starts all four processes. Press `Ctrl+C` to stop.

### 3. Run Individual Components

```bash
# Gateway only
python Gateway/run.py

# OrderBook only
python OrderBook/run.py

# Strategy only
python Strategy/run.py

# OrderManager only
python OrderManager/run.py
```

## Configuration

Edit `config.json` to configure the system:

```json
{
    "symbols": ["AAPL", "MSFT", "GOOG", "TSLA", "AMZN"],
    
    "Gateway": {
        "host": "localhost",
        "md_port": 8000,
        "news_port": 8001,
        "data_path": "data/market_data-1.csv"
    },
    
    "OrderBook": {
        "host": "localhost",
        "md_port": 8000,
        "shared_memory_name": "market_prices"
    },
    
    "Strategy": {
        "shared_memory_name": "market_prices",
        "order_manager_host": "localhost",
        "order_manager_port": 9000,
        "short_window": 5,
        "long_window": 20
    },
    
    "OrderManager": {
        "host": "localhost",
        "port": 9000
    }
}
```

## Project Structure

```
.
├── main.py                   # Main orchestrator
├── config.json              # Configuration
├── config.py                # Configuration loader
├── logger.py                # Logging setup
├── shared_memory_utils.py   # Shared memory wrapper
│
├── Gateway/                 # Market data & news feed
│   ├── __init__.py
│   ├── run.py
│   ├── stream.py
│   ├── serializers.py
│   ├── providers/
│   │   ├── market_data.py
│   │   ├── news.py
│   │   └── provider.py
│   └── test/
│
├── OrderBook/               # Shared memory manager
│   ├── __init__.py
│   ├── run.py
│   ├── feed_handler.py
│   ├── order_book.py
│   └── test/
│
├── Strategy/                # Signal generator (PLACEHOLDER)
│   ├── __init__.py
│   └── run.py
│
├── OrderManager/            # Order execution
│   ├── __init__.py         # Order class
│   ├── run.py
│   ├── server.py
│   ├── client.py
│   └── models.py
│
├── trading_lib/             # Trading strategies
│   ├── models.py
│   ├── strategy/
│   │   ├── base.py
│   │   ├── price_based_strategy.py
│   │   └── news_based_strategy.py
│   └── test/
│
├── examples/                # Usage examples
│   └── order_manager_example.py
│
├── data/
│   └── market_data-1.csv
│
└── logs/                    # Log files
```

## Testing

```bash
# Run all tests
pytest

# Run specific component tests
pytest Gateway/test/
pytest OrderBook/test/
pytest trading_lib/test/

# Run with coverage
pytest --cov=.
```

## Examples

### OrderManager Example

```bash
python examples/order_manager_example.py
```

Demonstrates:
- Starting OrderManager server
- Connecting client
- Sending orders

## Communication Protocols

### Market Data Protocol
- **Format:** `SYMBOL,PRICE*`
- **Example:** `AAPL,172.53*MSFT,325.20*`
- **Delimiter:** `*`

### News Protocol
- **Format:** `SYMBOL, SENTIMENT*`
- **Example:** `APPL,75*`
- **Range:** 0-100 (0=bearish, 100=bullish)

### Order Protocol
- **Format:** `TIMESTAMP,SIDE,QUANTITY,SYMBOL,PRICE*`
- **Example:** `1234567890.123,BUY,100,AAPL,172.53*`
- **Delimiter:** `*`

## Logs

Logs are written to `logs/` directory:
- `gateway.log`
- `orderbook.log`
- `strategy.log`
- `order_manager.log`
- `main.log`

## TODO

- [ ] Implement Strategy process
  - [x] Moving average crossover logic
  - [x] News-based signal logic
  - [x] Combined signal logic
  - [ ] Order generation
- [ ] Performance benchmarking
- [ ] Additional unit tests
- [ ] Performance report

## Development

### Adding a New Strategy

1. Implement strategy logic in `Strategy/run.py`
2. Read prices from `SharedPriceBook`
3. Subscribe to news feed
4. Use `OrderManagerClient` to send orders

```python
from shared_memory_utils import SharedPriceBook
from OrderManager.client import OrderManagerClient

# Read prices
book = SharedPriceBook(symbols, name="market_prices", create=False)
price, timestamp = book.read("AAPL")

# Send order
client = OrderManagerClient(host="localhost", port=9000)
client.connect()
client.place_order("AAPL", "BUY", 100, 172.53)
```

## License

Academic use only - FINM 32500 Assignment
