import socket
import os
from dotenv import load_dotenv
from server.core.controller import ServerController
from server.handlers.client_handler import ClientHandler
from shared.constants.network import NetworkConstants

load_dotenv()

class TetherServer:
    def __init__(self, host=None, port=None):
        self.host = host or os.getenv("SERVER_HOST", NetworkConstants.DEFAULT_HOST)
        self.port = int(port or os.getenv("SERVER_PORT", NetworkConstants.DEFAULT_PORT))
        self.controller = ServerController()
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        try:
            self.server_sock.bind((self.host, self.port))
            self.server_sock.listen(5)
            self.controller.logger.info(f"Server started on {self.host}:{self.port}")
            
            while True:
                client_sock, address = self.server_sock.accept()
                handler = ClientHandler(client_sock, address, self.controller)
                handler.start()
        except Exception as e:
            self.controller.logger.error(f"Server startup error: {e}")
        finally:
            self.server_sock.close()

if __name__ == "__main__":
    server = TetherServer()
    server.start()
