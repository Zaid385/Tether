# Tether Protocol Specification v1.0

## Overview
Tether uses a JSON-based packet protocol over raw TCP sockets. Each packet is a UTF-8 encoded JSON string, prefixed with a 4-byte big-endian integer indicating the length of the payload.

## Packet Structure
```
[4 bytes: length][JSON Payload]
```

## Common Fields
All packets should include:
- `type`: String identifying the action (e.g., "login", "msg_private").
- `timestamp`: ISO 8601 string.
- `payload`: Object containing the data.

## Packet Types

### Authentication
- `auth_login`: Request login.
- `auth_register`: Request registration.
- `auth_response`: Server response for auth actions.

### Messaging
- `msg_private`: Private message between two users.
- `msg_group`: Message sent to a group.
- `msg_receipt`: Read/Delivered receipt.

### Presence & Status
- `presence_update`: Online/Offline/Away status.
- `typing_indicator`: User is typing.

### Contacts & History
- `get_contacts`: Request sanitized list of all users.
- `contacts_list`: Server response with user list.
- `load_conversation`: Request message history with a specific user.
- `conversation_history`: Server response with chronological message list.

### File Transfer
- `file_init`: Request file transfer.
- `file_chunk`: Binary chunk of a file.
- `file_complete`: Signal end of transfer.

### Group Management
- `group_create`: Create a new group.
- `group_invite`: Invite user to group.
- `group_leave`: Leave a group.
