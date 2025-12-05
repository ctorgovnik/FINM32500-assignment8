from typing import List
from datetime import datetime

from OrderBook.feed_handler import FeedHandler
from logger import setup_logger
from shared_memory_utils import SharedPriceBook

class OrderBook:
    def __init__(self, config: dict):
        self.logger = setup_logger("order_book")
        
        try:
            symbols = config["symbols"]
        except KeyError:
            raise ValueError("Symbols are required")
        

        self.order_book = {symbol: [] for symbol in symbols}
        self.feed_handler = FeedHandler(config["host"], config["md_port"], config["news_port"])
        self.feed_handler.subscribe(self.on_market_data, "market_data")
        self.shared_price_book = SharedPriceBook(
            symbols, 
            name=config.get("shared_memory_name", "order_book"), 
            create=True
        )
        self.update_count = 0  # Track updates for periodic logging

    def on_market_data(self, data: bytes):
        try:
            # First update - log to confirm data flow
            if not hasattr(self, 'first_log_done'):
                self.logger.info("Receiving market data...")
                self.first_log_done = True
            
            # Decode and strip delimiter
            message = data.decode('utf-8').rstrip('*').strip()
            
            if not message:  # Empty message
                return
                
            parts = message.split(',')
            
            if len(parts) != 3:
                self.logger.error(f"Malformed market data (expected 3 fields, got {len(parts)}): '{message}'")
                return
            
            symbol = parts[0].strip()
            if not symbol:
                self.logger.error(f"Empty symbol in message: '{message}'")
                return
                
            try:
                price = float(parts[1].strip())
            except ValueError as e:
                self.logger.error(f"Invalid price '{parts[1]}' in message: '{message}'")
                return
            
            # Parse timestamp string to Unix epoch time
            timestamp_str = parts[2].strip()
            try:
                dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                timestamp = dt.timestamp()
            except ValueError:
                # If timestamp parsing fails, use current time
                timestamp = datetime.now().timestamp()
                self.logger.debug(f"Using current time for invalid timestamp: '{timestamp_str}'")

            self.shared_price_book.update(symbol, price, timestamp)
            
            # Log periodically to show activity without spam
            self.update_count += 1
            if self.update_count % 50 == 0:
                self.logger.info(f"Processed {self.update_count} updates (latest: {symbol} @ ${price:.2f})")
                self.logger.info(f"Processed {self.update_count} updates (latest: {symbol} @ ${price:.2f})")
        except Exception as e:
            self.logger.error(f"Unexpected error processing market data: {e}")
    
    def run(self):
        self.feed_handler.run()

    def shutdown(self):
        self.logger.info(f"Shared memory size: {self.shared_price_book.shared_memory_size()}")
        self.feed_handler.shutdown()
    
        