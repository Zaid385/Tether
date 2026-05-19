import bcrypt
from datetime import datetime
from server.database.mongo import MongoDB

class AuthService:
    def __init__(self, db: MongoDB):
        self.db = db

    def register_user(self, username, password):
        if self.db.users.find_one({"username": username}):
            return {"success": False, "message": "Username already exists"}

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_doc = {
            "username": username,
            "password": hashed_password,
            "created_at": datetime.now(),
            "status": "offline",
            "last_seen": datetime.now()
        }
        
        self.db.users.insert_one(user_doc)
        return {"success": True, "message": "Registration successful"}

    def login_user(self, username, password):
        user = self.db.users.find_one({"username": username})
        if not user:
            return {"success": False, "message": "Invalid username or password"}

        if bcrypt.checkpw(password.encode('utf-8'), user["password"]):
            # Update status to online
            self.db.users.update_one(
                {"username": username},
                {"$set": {"status": "online", "last_seen": datetime.now()}}
            )
            return {"success": True, "message": "Login successful"}
        
        return {"success": False, "message": "Invalid username or password"}

    def logout_user(self, username):
        self.db.users.update_one(
            {"username": username},
            {"$set": {"status": "offline", "last_seen": datetime.now()}}
        )
