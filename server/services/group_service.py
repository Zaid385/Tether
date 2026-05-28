import uuid
from datetime import datetime
from shared.protocol.packet import Packet
from shared.constants.network import ProtocolTypes
from shared.utils.network_utils import send_packet
from server.database.repository import GroupRepository, MessageRepository

class GroupService:
    def __init__(self, controller):
        self.controller = controller
        self.group_repo = GroupRepository(controller.db)
        self.message_repo = MessageRepository(controller.db)

    def handle_create_group(self, client_handler, packet):
        creator = client_handler.username
        group_name = packet.payload.get("group_name")
        initial_members = packet.payload.get("members", [])
        
        if not creator or not group_name:
            return

        # Ensure creator is in the members list
        if creator not in initial_members:
            initial_members.append(creator)

        group_id = str(uuid.uuid4())
        group_doc = {
            "group_id": group_id,
            "group_name": group_name,
            "creator": creator,
            "members": initial_members,
            "created_at": datetime.now()
        }
        
        self.group_repo.create_group(group_doc)
        
        # Notify all members
        notification_packet = Packet(ProtocolTypes.GROUP_CREATED, {
            "group_id": group_id,
            "group_name": group_name,
            "members": initial_members,
            "creator": creator
        })
        
        self._broadcast_to_group(group_id, notification_packet)

    def handle_group_message(self, client_handler, packet):
        sender = client_handler.username
        group_id = packet.payload.get("group_id")
        text = packet.payload.get("text")
        message_id = packet.payload.get("message_id") or str(uuid.uuid4())
        
        if not sender or not group_id or not text:
            return

        group = self.group_repo.get_group(group_id)
        if not group or sender not in group.get("members", []):
            return

        message_doc = {
            "message_id": message_id,
            "sender": sender,
            "recipient": group_id,
            "text": text,
            "timestamp": datetime.now(),
            "type": "group",
            "status": "SENT"
        }
        
        self.message_repo.save_message(message_doc)
        
        # Broadcast to group members
        forward_packet = Packet(ProtocolTypes.GROUP_MESSAGE, {
            "message_id": message_id,
            "group_id": group_id,
            "sender": sender,
            "text": text,
            "timestamp": message_doc["timestamp"].isoformat()
        })
        
        self._broadcast_to_group(group_id, forward_packet, exclude_user=sender)
        
        # Send ack to sender
        ack_packet = Packet(ProtocolTypes.RECEIPT_UPDATE, {
            "message_id": message_id,
            "status": "SENT",
            "recipient": group_id
        })
        send_packet(client_handler.client_sock, ack_packet)

    def handle_group_history(self, client_handler, packet):
        group_id = packet.payload.get("group_id")
        if not group_id: return
        
        history = self.message_repo.get_group_history(group_id)
        
        # Format timestamps
        for msg in history:
            if msg.get("timestamp"):
                msg["timestamp"] = msg["timestamp"].isoformat()
            if msg.get("delivered_at"):
                msg["delivered_at"] = msg["delivered_at"].isoformat()
            if msg.get("read_at"):
                msg["read_at"] = msg["read_at"].isoformat()

        response = Packet(ProtocolTypes.GROUP_HISTORY, {
            "group_id": group_id,
            "messages": history
        })
        send_packet(client_handler.client_sock, response)

    def _broadcast_to_group(self, group_id, packet, exclude_user=None):
        group = self.group_repo.get_group(group_id)
        if not group:
            return
            
        members = group.get("members", [])
        for member in members:
            if member == exclude_user:
                continue
            sock = self.controller.get_client_socket(member)
            if sock:
                try:
                    send_packet(sock, packet)
                except Exception as e:
                    self.controller.logger.error(f"Failed to route group msg to {member}: {e}")
