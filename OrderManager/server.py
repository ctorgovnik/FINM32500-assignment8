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

        # Create server socket with SO_REUSEADDR to allow port reuse
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Bind server socket to host and port
        try:
            self.server_socket.bind((self.host, self.port))
        except OSError as e:
            if e.errno == 48:  # Address already in use
                self.logger.warning(f"Port {self.port} is already in use. Attempting to clean up...")
                # Try to connect to see if something is actually using it
                try:
                    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    test_socket.connect((self.host, self.port))
                    test_socket.close()
                    self.logger.error(f"Port {self.port} is actively in use by another process")
                    raise
                except (ConnectionRefusedError, OSError):
                    # Port is bound but not accepting connections - wait a bit and retry
                    import time
                    time.sleep(0.5)
                    self.server_socket.bind((self.host, self.port))
            else:
                raise

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
            try:
                self.server_socket.settimeout(1.0)  # Allow periodic check of self.running
                client_socket, addr = self.server_socket.accept()
                with self.lock:
                    self.clients.append(client_socket)
                threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, addr), 
                    daemon=True
                ).start()
            except socket.timeout:
                continue  # Check self.running again
            except (OSError, socket.error) as e:
                if self.running:
                    self.logger.error(f"Error accepting client: {e}")
                break

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
        """Shutdown the server and clean up all resources"""
        if not self.running:
            return  # Already shut down
        
        self.running = False
        self.logger.info("Shutting down server...")
        
        # Close server socket first to stop accepting new connections
        if self.server_socket:
            try:
                self.server_socket.shutdown(socket.SHUT_RDWR)
            except (OSError, socket.error):
                pass  # Socket might already be closed
            
            try:
                self.server_socket.close()
            except Exception as e:
                self.logger.warning(f"Error closing server socket: {e}")
            finally:
                self.server_socket = None
        
        # Close all client connections
        with self.lock:
            client_count = len(self.clients)
            for client in self.clients:
                try:
                    client.shutdown(socket.SHUT_RDWR)
                except (OSError, socket.error):
                    pass
                try:
                    client.close()
                except Exception:
                    pass
            self.clients.clear()
            if client_count > 0:
                self.logger.info(f"Closed {client_count} client connection(s)")
        
        self.logger.info("Server shutdown complete")