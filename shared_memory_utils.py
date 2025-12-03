import numpy as np
from multiprocessing import Lock, shared_memory
import time

from logger import setup_logger

class SharedPriceBook:

    def __init__(self, symbols, name=None, create=True):
        self.logger = setup_logger("shared_price_book")
        self.symbols = symbols
        self.name = name
        self.num_symbols = len(symbols)
        self.lock = Lock()
        self._create = create  # Store for cleanup

        self.dtype = np.dtype(
            [
                ('symbol', 'U10'),
                ('price', 'f8'),
                ('timestamp', 'f8'),
            ]
        )

        self.size = self.num_symbols * self.dtype.itemsize

        if create:
            # Try to create, but if it already exists, unlink and recreate
            try:
                self.shm = shared_memory.SharedMemory(
                    create=True, 
                    size=self.size,
                    name=name or 'price_book'
                )
            except FileExistsError:
                # Shared memory exists from previous run - clean it up and recreate
                self.logger.warning(f"Shared memory '{name or 'price_book'}' already exists. Cleaning up...")
                try:
                    old_shm = shared_memory.SharedMemory(name=name or 'price_book', create=False)
                    old_shm.close()
                    old_shm.unlink()
                except Exception as e:
                    self.logger.warning(f"Error cleaning up old shared memory: {e}")
                
                # Now create fresh
                self.shm = shared_memory.SharedMemory(
                    create=True, 
                    size=self.size,
                    name=name or 'price_book'
                )

            self.prices = np.ndarray(
                shape=(self.num_symbols,),
                dtype=self.dtype,
                buffer=self.shm.buf
            )

            for i, sym in enumerate(self.symbols):
                self.prices[i] = (sym, 0.0, 0.0)
        
        else:
            self.shm = shared_memory.SharedMemory(
                name=name or 'price_book'
            )

            self.prices = np.ndarray(
                shape=(self.num_symbols,),
                dtype=self.dtype,
                buffer=self.shm.buf
            )
        
        self.symbol_index = {sym: i for i, sym in enumerate(self.symbols)}
    
    def update(self, symbol, price, timestamp):
        with self.lock:
            idx = self.symbol_index.get(symbol, None)
            if idx is None:
                self.logger.error(f"Symbol {symbol} not found in price book")
                return
            self.prices[idx]['price'] = price
            self.prices[idx]['timestamp'] = timestamp

    def read(self, symbol):
        with self.lock:
            idx = self.symbol_index.get(symbol, None)
            if idx is None:
                self.logger.error(f"Symbol {symbol} not found in price book")
                return None, None
            return self.prices[idx]['price'], self.prices[idx]['timestamp']
    
    def close(self):
        if hasattr(self, 'shm'):
            self.shm.close()
            self.logger.info(f"Closed shared memory: {self.name}")

    def unlink(self):
        if hasattr(self, 'shm'):
            self.shm.unlink()
            self.logger.info(f"Unlinked shared memory: {self.name}")
    
    def read_all(self):
        """Get all current prices as a dictionary"""
        with self.lock:
            return {
                str(self.prices[i]['symbol']): float(self.prices[i]['price'])
                for i in range(self.num_symbols)
            }
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if self._create:
            self.unlink()
        return False
    