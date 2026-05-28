from shared.protocol.packet import Packet
from shared.constants.network import ProtocolTypes
from shared.utils.network_utils import send_packet
from server.database.repository import UserRepository, MessageRepository

class ContactService:
    def __init__(self, controller):
        self.controller = controller
        self.user_repo = UserRepository(controller.db)

    def handle_get_contacts(self, client_handler, packet):
        username = client_handler.username
        if not username:
            return

        contacts = self.user_repo.get_all_users_sanitized(exclude_username=username)
        
        # Enrich with last message and unread count
        for contact in contacts:
            other = contact["username"]
            
            # Get last message
            query = {
                "$or": [
                    {"sender": username, "recipient": other, "type": "private"},
                    {"sender": other, "recipient": username, "type": "private"}
                ]
            }
            last_msg = self.controller.message_repo.collection.find_one(query, sort=[("timestamp", -1)])
            if last_msg:
                contact["last_message"] = last_msg["text"]
            else:
                contact["last_message"] = ""

            # Get unread count (received by current user from this contact)
            unread_query = {
                "sender": other,
                "recipient": username,
                "status": {"$ne": "READ"},
                "type": "private"
            }
            contact["unread_count"] = self.controller.message_repo.collection.count_documents(unread_query)
            
            if contact.get("last_seen"):
                contact["last_seen"] = contact["last_seen"].isoformat()

        response = Packet(ProtocolTypes.CONTACTS_LIST, {
            "contacts": contacts
        })
        send_packet(client_handler.client_sock, response)

class ConversationService:
    def __init__(self, controller):
        self.controller = controller
        self.message_repo = MessageRepository(controller.db)

    def handle_load_conversation(self, client_handler, packet):
        me = client_handler.username
        them = packet.payload.get("contact")
        
        if not me or not them:
            return

        history = self.message_repo.get_private_history(me, them)
        
        # Format timestamps
        for msg in history:
            if msg.get("timestamp"):
                msg["timestamp"] = msg["timestamp"].isoformat()
            if msg.get("delivered_at"):
                msg["delivered_at"] = msg["delivered_at"].isoformat()
            if msg.get("read_at"):
                msg["read_at"] = msg["read_at"].isoformat()

        response = Packet(ProtocolTypes.CONVERSATION_HISTORY, {
            "contact": them,
            "messages": history
        })
        send_packet(client_handler.client_sock, response)
