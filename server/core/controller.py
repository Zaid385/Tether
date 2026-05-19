import threading
import logging
from typing import Dict
from server.database.mongo import MongoDB

class ServerController:
    def __init__(self):
        self.active_clients = {}  # {username: socket}
        self.clients_lock = threading.Lock()
        self.db = MongoDB()
        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger("TetherServer")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def register_client(self, username: str, sock):
        with self.clients_lock:
            self.active_clients[username] = sock
            self.logger.info(f"User {username} logged in.")

    def unregister_client(self, username: str):
        with self.clients_lock:
            if username in self.active_clients:
                del self.active_clients[username]
                self.logger.info(f"User {username} logged out.")

    def get_client_socket(self, username: str):
        with self.clients_lock:
            return self.active_clients.get(username)

    def broadcast(self, packet, exclude_user=None):
        with self.clients_lock:
            for username, sock in self.active_clients.items():
                if username != exclude_user:
                    try:
                        from shared.utils.network_utils import send_packet
                        send_packet(sock, packet)
                    except Exception as e:
                        self.logger.error(f"Failed to broadcast to {username}: {e}")
