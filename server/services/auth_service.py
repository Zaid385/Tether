import bcrypt
from datetime import datetime
from server.database.mongo import MongoDB
from server.database.repository import UserRepository
from shared.protocol.packet import Packet
from shared.constants.network import ProtocolTypes
from shared.utils.network_utils import send_packet

class AuthService:
    def __init__(self, db: MongoDB):
        self.user_repo = UserRepository(db)

    def handle_login(self, client_handler, packet):
        username = packet.payload.get("username")
        password = packet.payload.get("password")
        
        result = self.login_user(username, password)
        
        if result["success"]:
            client_handler.username = username
            client_handler.controller.register_client(username, client_handler.client_sock)
        
        response = Packet(ProtocolTypes.AUTH_RESPONSE, result)
        send_packet(client_handler.client_sock, response)

    def handle_register(self, client_handler, packet):
        username = packet.payload.get("username")
        password = packet.payload.get("password")
        phone = packet.payload.get("phone")
        
        result = self.register_user(username, password, phone)
        
        if result["success"]:
            # Auto-login after successful registration
            client_handler.username = username
            client_handler.controller.register_client(username, client_handler.client_sock)
            # Update status to online immediately
            self.user_repo.update_status(username, "online", datetime.now())
        
        response = Packet(ProtocolTypes.AUTH_RESPONSE, result)
        send_packet(client_handler.client_sock, response)

    def register_user(self, username, password, phone):
        if self.user_repo.find_by_username(username):
            return {"success": False, "message": "Username already exists"}
        
        if self.user_repo.find_by_phone(phone):
            return {"success": False, "message": "Phone number already registered"}

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        user_doc = {
            "username": username,
            "password": hashed_password,
            "phone": phone,
            "created_at": datetime.now(),
            "status": "offline",
            "last_seen": datetime.now()
        }
        
        self.user_repo.create_user(user_doc)
        return {"success": True, "message": "Registration successful"}

    def login_user(self, username, password):
        user = self.user_repo.find_by_username(username)
        if not user:
            return {"success": False, "message": "Invalid username or password"}

        if bcrypt.checkpw(password.encode('utf-8'), user["password"]):
            self.user_repo.update_status(username, "online", datetime.now())
            return {"success": True, "message": "Login successful"}
        
        return {"success": False, "message": "Invalid username or password"}

    def logout_user(self, username):
        self.user_repo.update_status(username, "offline", datetime.now())
