from shared.protocol.packet import Packet
from shared.constants.network import ProtocolTypes
from shared.utils.network_utils import send_packet

class NotificationService:
    def __init__(self, controller):
        self.controller = controller

    def push_notification(self, recipient: str, title: str, body: str, severity: str = "info"):
        """Centralized method to push notifications to clients."""
        sock = self.controller.get_client_socket(recipient)
        if sock:
            packet = Packet(ProtocolTypes.NOTIFICATION, {
                "title": title,
                "body": body,
                "severity": severity
            })
            try:
                send_packet(sock, packet)
            except Exception as e:
                self.controller.logger.error(f"Failed to send notification to {recipient}: {e}")

    def broadcast_notification(self, title: str, body: str, severity: str = "info"):
        packet = Packet(ProtocolTypes.NOTIFICATION, {
            "title": title,
            "body": body,
            "severity": severity
        })
        self.controller.broadcast(packet)
