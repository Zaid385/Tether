class NetworkConstants:
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 5555
    BUFFER_SIZE = 4096
    HEADER_SIZE = 4  # 4 bytes for payload length
    TIMEOUT = 30.0

class ProtocolTypes:
    # Auth
    AUTH_LOGIN = "auth_login"
    AUTH_REGISTER = "auth_register"
    AUTH_RESPONSE = "auth_response"
    
    # Messaging
    MSG_PRIVATE = "msg_private"
    MSG_GROUP = "msg_group"
    MSG_RECEIPT = "msg_receipt"
    
    # Presence
    PRESENCE_UPDATE = "presence_update"
    TYPING_START = "typing_start"
    TYPING_STOP = "typing_stop"
    
    # Receipts
    MSG_DELIVERED = "msg_delivered"
    MSG_READ = "msg_read"
    RECEIPT_UPDATE = "receipt_update"
    
    # Contacts & History
    GET_CONTACTS = "get_contacts"
    CONTACTS_LIST = "contacts_list"
    LOAD_CONVERSATION = "load_conversation"
    CONVERSATION_HISTORY = "conversation_history"
    
    # Groups
    CREATE_GROUP = "create_group"
    GROUP_CREATED = "group_created"
    JOIN_GROUP = "join_group"
    LEAVE_GROUP = "leave_group"
    GROUP_MESSAGE = "group_message"
    GROUP_HISTORY = "group_history"
    GROUP_PRESENCE_UPDATE = "group_presence_update"
    
    # Notifications
    NOTIFICATION = "notification"
    
    # Search
    SEARCH_REQUEST = "search_request"
    SEARCH_RESULTS = "search_results"
    
    # Files
    FILE_TRANSFER_REQUEST = "file_transfer_request"
    FILE_TRANSFER_ACCEPT = "file_transfer_accept"
    FILE_TRANSFER_REJECT = "file_transfer_reject"
    FILE_TRANSFER_CHUNK = "file_transfer_chunk"
    FILE_TRANSFER_COMPLETE = "file_transfer_complete"
    FILE_TRANSFER_PROGRESS = "file_transfer_progress"
