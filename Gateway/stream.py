import socket
from typing import List
import threading

from providers.provider import Provider

class Stream:
    def __init__(self, provider: Provider, port: int, delimiter: bytes = b'*'):
        self.provider = provider
        self.port = port
        self.delimiter = delimiter
        self.clients: List[socket.socket] = []
        self.lock = threading.Lock()


    def accept_clients(self, server_socket: socket.socket):
        """
        Accepts client connections and adds them to the clients list
        """
        while True:
            try:
                client_socket, addr = server_socket.accept()
                with self.lock:
                    self.clients.append(client_socket)
            except Exception as e:
                print(f"Error accepting client: {e}")
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
                print(f"Error broadcasting data to client: {e}")
                dead_clients.append(client)
        
        # Remove dead clients
        if dead_clients:
            with self.lock:
                self.clients = [client for client in self.clients if client not in dead_clients]
    
    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', self.port))
        server_socket.listen(5)
        # Log the server socket is listening

        # Start background thread to accept clients
        accept_thread = threading.Thread(
            target=self.accept_clients,
            args=(server_socket,),
            daemon=True,
        )
        accept_thread.start()

        # Start main loop to broadcast data to clients
        try:
            while True:
                data = self.provider.get_next_data()
                self.broadcast(data)
        except KeyboardInterrupt:
            print("Shutting down...")
        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            server_socket.close()
            with self.lock:
                for client in self.clients:
                    client.close()
            print("Gateway shut down")