from datetime import datetime
from shared.protocol.packet import Packet
from shared.constants.network import ProtocolTypes
from server.database.repository import UserRepository

class PresenceService:
    def __init__(self, controller):
        self.controller = controller
        self.user_repo = UserRepository(controller.db)

    def broadcast_status(self, username, status):
        packet = Packet(ProtocolTypes.PRESENCE_UPDATE, {
            "username": username,
            "status": status,
            "timestamp": datetime.now().isoformat()
        })
        self.controller.broadcast(packet, exclude_user=username)

    def handle_presence_update(self, client_handler, packet):
        # Allow client to manually set status if needed
        status = packet.payload.get("status")
        username = client_handler.username
        if username:
            self.user_repo.update_status(username, status, datetime.now())
            self.broadcast_status(username, status)
