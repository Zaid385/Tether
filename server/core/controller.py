import threading
import logging
from typing import Dict
from server.database.mongo import MongoDB
from server.database.repository import UserRepository, MessageRepository
from server.core.dispatcher import PacketDispatcher

class ServerController:
    def __init__(self):
        self.db = MongoDB()
        self.user_repo = UserRepository(self.db)
        self.message_repo = MessageRepository(self.db)
        
        self.active_clients = {}  # {username: socket}
        self.clients_lock = threading.RLock() # Use RLock to prevent deadlocks
        self.logger = self._setup_logger()
        
        self.dispatcher = PacketDispatcher(self)
        self._register_handlers()
        
        # Cleanup: Force all users to offline on server startup to clear stale ghost sessions
        self._cleanup_ghost_statuses()

    def _cleanup_ghost_statuses(self):
        try:
            from datetime import datetime
            self.user_repo.collection.update_many(
                {}, 
                {"$set": {"status": "offline", "last_seen": datetime.now()}}
            )
            self.logger.info("Database cleanup: All user statuses reset to offline.")
        except Exception as e:
            self.logger.error(f"Failed to cleanup ghost statuses: {e}")

    def _setup_logger(self):
        logger = logging.getLogger("TetherServer")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _register_handlers(self):
        from shared.constants.network import ProtocolTypes
        from server.services.auth_service import AuthService
        from server.services.message_service import MessageService
        from server.services.presence_service import PresenceService
        from server.services.contact_service import ContactService, ConversationService
        from server.services.typing_service import TypingService
        from server.services.group_service import GroupService
        from server.services.file_transfer_service import FileTransferService
        from server.services.search_service import SearchService
        
        auth_service = AuthService(self.db)
        message_service = MessageService(self)
        self.presence_service = PresenceService(self)
        contact_service = ContactService(self)
        conv_service = ConversationService(self)
        typing_service = TypingService(self)
        group_service = GroupService(self)
        file_service = FileTransferService(self)
        search_service = SearchService(self)
        
        self.dispatcher.register_handler(ProtocolTypes.AUTH_LOGIN, auth_service.handle_login)
        self.dispatcher.register_handler(ProtocolTypes.AUTH_REGISTER, auth_service.handle_register)
        self.dispatcher.register_handler(ProtocolTypes.MSG_PRIVATE, message_service.handle_private_message)
        self.dispatcher.register_handler(ProtocolTypes.PRESENCE_UPDATE, self.presence_service.handle_presence_update)
        self.dispatcher.register_handler(ProtocolTypes.GET_CONTACTS, contact_service.handle_get_contacts)
        self.dispatcher.register_handler(ProtocolTypes.LOAD_CONVERSATION, conv_service.handle_load_conversation)
        
        # Typing
        self.dispatcher.register_handler(ProtocolTypes.TYPING_START, typing_service.handle_typing_event)
        self.dispatcher.register_handler(ProtocolTypes.TYPING_STOP, typing_service.handle_typing_event)
        
        # Receipts
        self.dispatcher.register_handler(ProtocolTypes.MSG_DELIVERED, message_service.handle_receipt)
        self.dispatcher.register_handler(ProtocolTypes.MSG_READ, message_service.handle_receipt)

        # Groups
        self.dispatcher.register_handler(ProtocolTypes.CREATE_GROUP, group_service.handle_create_group)
        self.dispatcher.register_handler(ProtocolTypes.GROUP_MESSAGE, group_service.handle_group_message)
        self.dispatcher.register_handler(ProtocolTypes.GROUP_HISTORY, group_service.handle_group_history)
        
        # Files
        self.dispatcher.register_handler(ProtocolTypes.FILE_TRANSFER_REQUEST, file_service.handle_transfer_request)
        self.dispatcher.register_handler(ProtocolTypes.FILE_TRANSFER_ACCEPT, file_service.handle_transfer_accept)
        self.dispatcher.register_handler(ProtocolTypes.FILE_TRANSFER_CHUNK, file_service.handle_transfer_chunk)
        self.dispatcher.register_handler(ProtocolTypes.FILE_TRANSFER_COMPLETE, file_service.handle_transfer_complete)
        
        # Search
        self.dispatcher.register_handler(ProtocolTypes.SEARCH_REQUEST, search_service.handle_search)

    def register_client(self, username: str, sock):
        with self.clients_lock:
            self.active_clients[username] = sock
            self.logger.info(f"User {username} logged in.")
            self.presence_service.broadcast_status(username, "online")

    def unregister_client(self, username: str):
        with self.clients_lock:
            if username in self.active_clients:
                del self.active_clients[username]
                self.logger.info(f"User {username} logged out.")
                self.presence_service.broadcast_status(username, "offline")

    def get_client_socket(self, username: str):
        with self.clients_lock:
            return self.active_clients.get(username)

    def broadcast(self, packet, exclude_user=None):
        with self.clients_lock:
            for username, sock in self.active_clients.items():
                if username != exclude_user:
                    try:
                        from shared.utils.network_utils import send_packet
                        send_packet(sock, packet)
                    except Exception as e:
                        self.logger.error(f"Failed to broadcast to {username}: {e}")
