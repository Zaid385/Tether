from typing import Optional, List, Any
from server.database.mongo import MongoDB

class UserRepository:
    def __init__(self, db: MongoDB):
        self.collection = db.users
        # Ensure indexes on username and phone
        self.collection.create_index("username", unique=True)
        # Use sparse=True because existing users might have null phone numbers
        self.collection.create_index("phone", unique=True, sparse=True)
        # Text index for username search
        self.collection.create_index([("username", "text")])

    def find_by_username(self, username: str) -> Optional[dict]:
        return self.collection.find_one({"username": username})

    def find_by_phone(self, phone: str) -> Optional[dict]:
        return self.collection.find_one({"phone": phone})

    def get_all_users_sanitized(self, exclude_username: str) -> List[dict]:
        """Returns public profile data for all users except the excluded one."""
        projection = {
            "username": 1,
            "status": 1,
            "last_seen": 1,
            "_id": 0
        }
        return list(self.collection.find({"username": {"$ne": exclude_username}}, projection))

    def create_user(self, user_doc: dict):
        return self.collection.insert_one(user_doc)

    def update_status(self, username: str, status: str, last_seen: Any):
        self.collection.update_one(
            {"username": username},
            {"$set": {"status": status, "last_seen": last_seen}}
        )

class MessageRepository:
    def __init__(self, db: MongoDB):
        self.collection = db.messages
        # Ensure indexes for fast history lookup and status updates
        self.collection.create_index([("sender", 1), ("recipient", 1), ("timestamp", 1)])
        self.collection.create_index("message_id", unique=True, sparse=True)
        # Text index for search
        self.collection.create_index([("text", "text")])

    def save_message(self, message_doc: dict):
        return self.collection.insert_one(message_doc)

    def update_message_status(self, message_id: str, status: str, timestamp_field: str, timestamp: Any):
        """Updates the status and specific timestamp (delivered_at/read_at) of a message."""
        update_doc = {
            "$set": {
                "status": status,
                timestamp_field: timestamp
            }
        }
        return self.collection.update_one({"message_id": message_id}, update_doc)

    def mark_all_read(self, sender: str, recipient: str, timestamp: Any):
        """Marks all messages from sender to recipient as READ."""
        query = {
            "sender": sender,
            "recipient": recipient,
            "status": {"$ne": "READ"}
        }
        update = {
            "$set": {
                "status": "READ",
                "read_at": timestamp
            }
        }
        return self.collection.update_many(query, update)

    def get_private_history(self, user1: str, user2: str, limit: int = 50) -> List[dict]:
        query = {
            "$or": [
                {"sender": user1, "recipient": user2, "type": "private"},
                {"sender": user2, "recipient": user1, "type": "private"}
            ]
        }
        # Sort by timestamp ascending for the client to display in order
        messages = list(self.collection.find(query, {"_id": 0}).sort("timestamp", 1).limit(limit))
        return messages

    def get_group_history(self, group_id: str, limit: int = 50) -> List[dict]:
        query = {
            "recipient": group_id,
            "type": "group"
        }
        return list(self.collection.find(query, {"_id": 0}).sort("timestamp", 1).limit(limit))

    def search_messages(self, current_user: str, term: str) -> List[dict]:
        """Search messages belonging to current user matching term."""
        query = {
            "$text": {"$search": term},
            "$or": [{"sender": current_user}, {"recipient": current_user}]
        }
        return list(self.collection.find(query, {"_id": 0}).sort("timestamp", -1).limit(20))

class GroupRepository:
    def __init__(self, db: MongoDB):
        self.collection = db.groups
        self.collection.create_index("group_id", unique=True)
        self.collection.create_index([("group_name", "text")])

    def create_group(self, group_doc: dict):
        return self.collection.insert_one(group_doc)

    def get_group(self, group_id: str) -> Optional[dict]:
        return self.collection.find_one({"group_id": group_id}, {"_id": 0})

    def get_groups_for_user(self, username: str) -> List[dict]:
        return list(self.collection.find({"members": username}, {"_id": 0}))

    def add_member(self, group_id: str, username: str):
        return self.collection.update_one(
            {"group_id": group_id},
            {"$addToSet": {"members": username}}
        )

    def remove_member(self, group_id: str, username: str):
        return self.collection.update_one(
            {"group_id": group_id},
            {"$pull": {"members": username}}
        )

    def search_groups(self, term: str) -> List[dict]:
        return list(self.collection.find({"$text": {"$search": term}}, {"_id": 0}))
