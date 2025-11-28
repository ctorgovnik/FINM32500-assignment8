import socket
import time
from OrderManager import Order

from logger import setup_logger

class OrderManagerClient:
    """Client for sending orders to OrderManager"""
    def __init__(self, host: str, port: int):
        self.logger = setup_logger("order_manager_client")
        self.host = host
        self.port = port
        self.connected = False


    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.logger.info(f"Connected to OrderManager at {self.host}:{self.port}")
            self.connected = True
        except Exception as e:
            self.logger.error(f"Error connecting to OrderManager: {e}")
            return False
        return True

    def place_order(self, symbol: str, side: str, quantity: int, price: float) -> bool:
        try:
            from OrderManager import Side
            order = Order(
                symbol=symbol,
                side=Side(side.upper()),
                quantity=quantity,
                price=price,
                timestamp=time.time()
            )
            return self.send_order(order)
        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            return False

    def send_order(self, order: Order) -> bool:
        if not self.connected:
            self.logger.error("Not connected to OrderManager")
            return False
        try:
            message = order.to_bytes()
            self.socket.sendall(message)
            self.logger.info(f"Sent order: {order}")
            return True
        except Exception as e:
            self.logger.error(f"Error sending order: {e}")
            self.connected = False
            return False


    def disconnect(self):
        """Disconnect from OrderManager"""
        if self.socket:
            try:
                self.socket.close()
                self.logger.info("Disconnected from OrderManager")
            except:
                pass
            finally:
                self.connected = False
                self.socket = None