from shared.protocol.packet import Packet
from shared.constants.network import ProtocolTypes
from shared.utils.network_utils import send_packet

class TypingService:
    def __init__(self, controller):
        self.controller = controller

    def handle_typing_event(self, client_handler, packet):
        recipient_username = packet.payload.get("recipient")
        sender_username = client_handler.username
        
        if not sender_username or not recipient_username:
            return

        # Ephemeral event - just route it to the recipient if online
        recipient_sock = self.controller.get_client_socket(recipient_username)
        if recipient_sock:
            forward_packet = Packet(packet.type, {
                "sender": sender_username
            })
            try:
                send_packet(recipient_sock, forward_packet)
            except Exception as e:
                self.controller.logger.error(f"Failed to route typing event to {recipient_username}: {e}")
