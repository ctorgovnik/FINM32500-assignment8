import socket
import threading

from logger import setup_logger
from OrderManager import Order

class Server:
    def __init__(self, config: dict):
        self.logger = setup_logger("order_manager_server")
        self.host = config["host"]
        self.port = config["order_manager_port"]
        self.running = True

        self.logger.info(f"Server attempting to listen on {self.host}:{self.port}")

        # Create server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind server socket to host and port
        self.server_socket.bind((self.host, self.port))

        # Start listening for clients
        self.server_socket.listen(5)
        self.logger.info(f"Server listening on {self.host}:{self.port}")

        self.clients = []
        self.lock = threading.Lock()
    
    def run(self):
        """Start accepting client connections"""
        self.logger.info(f"OrderManager listening on {self.host}:{self.port}")
        self.accept_clients()

    def accept_clients(self):
        while self.running:
            client_socket, addr = self.server_socket.accept()
            with self.lock:
                self.clients.append(client_socket)
            threading.Thread(
                target=self.handle_client,
                args=(client_socket, addr), 
                daemon=True
            ).start()

    def handle_client(self, client_socket: socket.socket, addr: tuple):
        """Handle client connection"""
        self.logger.info(f"Client connected from {addr}")
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    self.logger.info(f"Client {addr} disconnected")
                    break
                self.route_order(data)
        except Exception as e:
            self.logger.error(f"Error handling client {addr}: {e}")
        finally:
            client_socket.close()
            with self.lock:
                self.clients.remove(client_socket)
        self.logger.info(f"Client {addr} disconnected")

    def route_order(self, data: bytes):
        try:
            order = Order.from_bytes(data)
            self.logger.info(f"Received order: {order}")

            self._execute_order(order)
        except Exception as e:
            self.logger.error(f"Error routing order: {e}")
    
    def _execute_order(self, order: Order):
        try:
            self.logger.info(f"Executing order: {order}")
        except Exception as e:
            self.logger.error(f"Error executing order: {e}")
    
    def shutdown(self):
        """Shutdown the server"""
        self.running = False
        self.server_socket.close()
        self.logger.info("Server shutdown")