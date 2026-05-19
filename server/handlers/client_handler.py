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
                
                self.handle_packet(packet)
        except Exception as e:
            self.controller.logger.error(f"Error handling client {self.address}: {e}")
        finally:
            self.cleanup()

    def handle_packet(self, packet):
        ptype = packet.type
        
        if ptype == ProtocolTypes.AUTH_LOGIN:
            self.handle_login(packet)
        elif ptype == ProtocolTypes.AUTH_REGISTER:
            self.handle_register(packet)
        else:
            self.controller.logger.warning(f"Unhandled packet type: {ptype}")

    def handle_login(self, packet):
        username = packet.payload.get("username")
        password = packet.payload.get("password")
        
        result = self.auth_service.login_user(username, password)
        
        if result["success"]:
            self.username = username
            self.controller.register_client(username, self.client_sock)
        
        response = Packet(ProtocolTypes.AUTH_RESPONSE, result)
        send_packet(self.client_sock, response)

    def handle_register(self, packet):
        username = packet.payload.get("username")
        password = packet.payload.get("password")
        
        result = self.auth_service.register_user(username, password)
        
        response = Packet(ProtocolTypes.AUTH_RESPONSE, result)
        send_packet(self.client_sock, response)

    def cleanup(self):
        self.running = False
        if self.username:
            self.auth_service.logout_user(self.username)
            self.controller.unregister_client(self.username)
        self.client_sock.close()
        self.controller.logger.info(f"Connection closed for {self.address}")
