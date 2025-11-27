import socket
from typing import List, Optional
import threading
import logging
import time

from Gateway.providers.provider import Provider

class Stream:
    def __init__(self, provider: Provider, port: int, delimiter: bytes = b'*', logger: Optional[logging.Logger] = None):
        self.provider = provider
        self.port = port
        self.delimiter = delimiter
        self.clients: List[socket.socket] = []
        self.lock = threading.Lock()
        self.shutdown_event = threading.Event()
        self.server_socket = None
        self.accept_thread = None
        self._shutdown_called = False
        self.logger = logger or logging.getLogger(f"stream_{port}")


    def accept_clients(self, server_socket: socket.socket):
        """
        Accepts client connections and adds them to the clients list
        """
        while not self.shutdown_event.is_set():
            try:
                server_socket.settimeout(1.0)  # Allow periodic check of shutdown_event
                client_socket, addr = server_socket.accept()
                with self.lock:
                    self.clients.append(client_socket)
                self.logger.info(f"Client connected from {addr} on port {self.port}")
            except socket.timeout:
                continue  # Check shutdown_event again
            except (OSError, socket.error) as e:
                if not self.shutdown_event.is_set():
                    self.logger.error(f"Error accepting client on port {self.port}: {e}")
                break

    def broadcast(self, data: bytes):
        if not data:
            return
        
        if not data.endswith(self.delimiter):
            data = data + self.delimiter
        
        with self.lock:
            clients_copy = self.clients.copy()
        
        dead_clients = []
        for client in clients_copy:
            try:
                client.sendall(data)
            except Exception as e:
                self.logger.warning(f"Error broadcasting data to client on port {self.port}: {e}")
                dead_clients.append(client)
        
        # Remove dead clients
        if dead_clients:
            with self.lock:
                self.clients = [client for client in self.clients if client not in dead_clients]
    
    def run(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(5)
            self.logger.info(f"Server socket listening on port {self.port}")
        except Exception as e:
            self.logger.error(f"Error setting up server socket on port {self.port}: {e}", exc_info=True)
            self.shutdown_event.set()
            self.shutdown()  # Ensure cleanup even on setup failure
            return

        # Start background thread to accept clients
        self.accept_thread = threading.Thread(
            target=self.accept_clients,
            args=(self.server_socket,),
            daemon=True,
        )
        self.accept_thread.start()
        self.logger.debug(f"Started accept thread for port {self.port}")

        # Start main loop to broadcast data to clients
        try:
            while not self.shutdown_event.is_set():
                data = self.provider.get_next_data()
                if data is None:
                    # If provider returns None, wait a bit before checking again
                    self.shutdown_event.wait(0.1)
                    continue
                self.broadcast(data)
        except KeyboardInterrupt:
            self.logger.info(f"Received KeyboardInterrupt on port {self.port}, shutting down...")
        except Exception as e:
            self.logger.error(f"Error in main loop on port {self.port}: {e}", exc_info=True)
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Clean shutdown of the stream - ensures port is released"""
        # Make shutdown idempotent
        if self._shutdown_called:
            return
        self._shutdown_called = True
        
        self.logger.debug(f"Starting shutdown for stream on port {self.port}")
        self.shutdown_event.set()
        
        # Close server socket first to interrupt accept() calls and release the port
        if self.server_socket:
            try:
                # Shutdown the socket before closing to ensure clean release
                self.server_socket.shutdown(socket.SHUT_RDWR)
            except (OSError, socket.error):
                # Socket might already be closed or in a bad state
                pass
            
            try:
                self.server_socket.close()
                self.logger.debug(f"Closed server socket on port {self.port}")
            except Exception as e:
                self.logger.warning(f"Error closing server socket on port {self.port}: {e}")
            finally:
                self.server_socket = None
        
        # Wait for accept thread to finish (it should exit quickly after socket is closed)
        if self.accept_thread and self.accept_thread.is_alive():
            self.accept_thread.join(timeout=1.0)
            if self.accept_thread.is_alive():
                self.logger.warning(f"Accept thread on port {self.port} did not finish within timeout")
        
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
                self.logger.info(f"Closed {client_count} client connection(s) on port {self.port}")
        
        # Small delay to ensure OS releases the port
        time.sleep(0.1)
        
        self.logger.info(f"Stream on port {self.port} shut down and port released")