import threading
from shared.utils.network_utils import receive_packet, send_packet
from shared.protocol.packet import Packet
from shared.constants.network import ProtocolTypes
from server.services.auth_service import AuthService

class ClientHandler(threading.Thread):
    def __init__(self, client_sock, address, controller):
        super().__init__()
        self.client_sock = client_sock
        self.address = address
        self.controller = controller
        self.auth_service = AuthService(controller.db)
        self.username = None
        self.running = True

    def run(self):
        self.controller.logger.info(f"New connection from {self.address}")
        try:
            while self.running:
                packet = receive_packet(self.client_sock)
                if packet is None:
                    break
                
                self.controller.dispatcher.dispatch(self, packet)
        except Exception as e:
            self.controller.logger.error(f"Error handling client {self.address}: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        self.running = False
        if self.username:
            self.auth_service.logout_user(self.username)
            self.controller.unregister_client(self.username)
        self.client_sock.close()
        self.controller.logger.info(f"Connection closed for {self.address}")
