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
    TYPING_INDICATOR = "typing_indicator"
    
    # Files
    FILE_INIT = "file_init"
    FILE_CHUNK = "file_chunk"
    FILE_COMPLETE = "file_complete"
    
    # Groups
    GROUP_CREATE = "group_create"
    GROUP_INVITE = "group_invite"
    GROUP_LEAVE = "group_leave"
