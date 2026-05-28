from shared.protocol.packet import Packet
from shared.constants.network import ProtocolTypes
from shared.utils.network_utils import send_packet

class SearchService:
    def __init__(self, controller):
        self.controller = controller

    def handle_search(self, client_handler, packet):
        term = packet.payload.get("term")
        username = client_handler.username
        
        if not term or not username:
            return

        # Parallel search across collections
        # 1. Users (excluding self)
        user_matches = self.controller.user_repo.collection.find({
            "username": {"$regex": term, "$options": "i"},
            "username": {"$ne": username}
        }, {"_id": 0, "username": 1, "status": 1}).limit(10)
        
        # 2. Groups
        group_matches = self.controller.group_repo.collection.find({
            "group_name": {"$regex": term, "$options": "i"},
            "members": username
        }, {"_id": 0, "group_name": 1, "group_id": 1}).limit(10)
        
        # 3. Messages
        msg_matches = self.controller.message_repo.collection.find({
            "$text": {"$search": term},
            "$or": [{"sender": username}, {"recipient": username}]
        }, {"_id": 0}).sort("timestamp", -1).limit(10)

        # Format timestamps for JSON
        msgs = list(msg_matches)
        for m in msgs:
            if m.get("timestamp"): m["timestamp"] = m["timestamp"].isoformat()

        response = Packet(ProtocolTypes.SEARCH_RESULTS, {
            "users": list(user_matches),
            "groups": list(group_matches),
            "messages": msgs
        })
        send_packet(client_handler.client_sock, response)
