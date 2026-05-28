import uuid
from datetime import datetime
from shared.protocol.packet import Packet
from shared.constants.network import ProtocolTypes
from shared.utils.network_utils import send_packet
from server.database.repository import MessageRepository

class MessageService:
    def __init__(self, controller):
        self.controller = controller
        self.message_repo = MessageRepository(controller.db)

    def handle_private_message(self, client_handler, packet):
        recipient_username = packet.payload.get("recipient")
        message_text = packet.payload.get("text")
        # Use client-provided ID if available to sync receipts perfectly
        message_id = packet.payload.get("message_id") or str(uuid.uuid4())
        sender_username = client_handler.username
        
        if not sender_username:
            return

        message_doc = {
            "message_id": message_id,
            "sender": sender_username,
            "recipient": recipient_username,
            "text": message_text,
            "timestamp": datetime.now(),
            "type": "private",
            "status": "SENT"
        }
        
        # Save to DB
        self.message_repo.save_message(message_doc)
        
        # Route to recipient if online
        recipient_sock = self.controller.get_client_socket(recipient_username)
        if recipient_sock:
            forward_packet = Packet(ProtocolTypes.MSG_PRIVATE, {
                "message_id": message_id,
                "sender": sender_username,
                "text": message_text,
                "timestamp": message_doc["timestamp"].isoformat()
            })
            try:
                send_packet(recipient_sock, forward_packet)
            except Exception as e:
                self.controller.logger.error(f"Failed to route message to {recipient_username}: {e}")
        
        # Notify sender that message is SENT (optional but good for syncing IDs)
        ack_packet = Packet(ProtocolTypes.RECEIPT_UPDATE, {
            "message_id": message_id,
            "status": "SENT",
            "recipient": recipient_username
        })
        send_packet(client_handler.client_sock, ack_packet)

    def handle_receipt(self, client_handler, packet):
        """Handles DELIVERED or READ receipts from clients."""
        m_type = packet.type
        message_id = packet.payload.get("message_id")
        # sender_of_msg is the one who originally sent the message being acknowledged
        sender_of_msg = packet.payload.get("sender") 
        
        status = "DELIVERED" if m_type == ProtocolTypes.MSG_DELIVERED else "READ"
        field = "delivered_at" if m_type == ProtocolTypes.MSG_DELIVERED else "read_at"
        
        # Update DB
        self.message_repo.update_message_status(message_id, status, field, datetime.now())
        
        # Route receipt back to the original sender so their UI updates
        sender_sock = self.controller.get_client_socket(sender_of_msg)
        if sender_sock:
            receipt_packet = Packet(ProtocolTypes.RECEIPT_UPDATE, {
                "message_id": message_id,
                "status": status,
                "recipient": client_handler.username # The one who is sending the receipt
            })
            try:
                send_packet(sender_sock, receipt_packet)
            except Exception as e:
                self.controller.logger.error(f"Failed to route receipt to {sender_of_msg}: {e}")
