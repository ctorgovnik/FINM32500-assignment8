from typing import Callable, List, Dict
import time
import socket
import threading

class FeedHandler:
    def __init__(self, host: str, md_port: int, news_port: int):
        self.host = host
        self.md_port = md_port
        self.news_port = news_port
        self.subscribers: Dict[str, List[Callable]] = {
            "market_data": [],
            "news": []
        }
        self.socket_to_feed_type: Dict[socket.socket, str] = {}

        self.md_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.md_client_socket.connect((self.host, self.md_port))
        self.socket_to_feed_type[self.md_client_socket] = "market_data"

        self.news_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.news_client_socket.connect((self.host, self.news_port))
        self.socket_to_feed_type[self.news_client_socket] = "news"

    def run(self):
        threading.Thread(target=self.listen, args=(self.md_client_socket,), daemon=True).start()
        threading.Thread(target=self.listen, args=(self.news_client_socket,), daemon=True).start()
    
    def listen(self, socket: socket.socket):
        feed_type = self.socket_to_feed_type[socket]
        while True:
            data = socket.recv(1024)
            if data:
                for subscriber in self.subscribers[feed_type]:
                    subscriber(data)
            else:
                break
    
    def disconnect(self, socket: socket.socket):
        socket.close()
        self.socket_to_feed_type.pop(socket)
        self.subscribers[self.socket_to_feed_type[socket]].clear()

    def subscribe(self, callback: Callable, feed_type: str):
        
        if feed_type not in self.subscribers:
            raise ValueError(f"Invalid feed type: {feed_type}")
        self.subscribers[feed_type].append(callback)
    
    
    def shutdown(self):
        self.disconnect(self.md_client_socket)
        self.disconnect(self.news_client_socket)
