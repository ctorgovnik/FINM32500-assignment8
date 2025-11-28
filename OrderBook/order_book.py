from typing import List

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
        self.shared_price_book = SharedPriceBook(symbols, name="order_book", create=True)

    def on_market_data(self, data: bytes):
        try:
            symbol = data.decode('utf-8').split(',')[0]
            price = float(data.decode('utf-8').split(',')[1])
            timestamp = float(data.decode('utf-8').split(',')[2])

            self.shared_price_book.update(symbol, price, timestamp)
            self.logger.info(f"Updated shared price book: {symbol} {price} {timestamp}")
        except Exception as e:
            self.logger.error(f"Error updating shared price book: {e}")
    
    def run(self):
        self.feed_handler.run()

    def shutdown(self):
        self.feed_handler.shutdown()
    
        