import os
import uuid
import base64
from shared.protocol.packet import Packet
from shared.constants.network import ProtocolTypes
from shared.utils.network_utils import send_packet

class FileTransferService:
    def __init__(self, controller):
        self.controller = controller
        self.active_transfers = {} # {file_id: session_data}
        self.storage_dir = os.path.join(os.getcwd(), "server_data", "files")
        os.makedirs(self.storage_dir, exist_ok=True)

    def handle_transfer_request(self, client_handler, packet):
        sender = client_handler.username
        recipient = packet.payload.get("recipient")
        filename = packet.payload.get("filename")
        filesize = packet.payload.get("filesize")
        
        if not sender or not recipient or not filename:
            return

        file_id = str(uuid.uuid4())
        
        self.active_transfers[file_id] = {
            "sender": sender,
            "recipient": recipient,
            "filename": filename,
            "filesize": filesize,
            "received_bytes": 0,
            "status": "pending",
            "filepath": os.path.join(self.storage_dir, f"{file_id}_{filename}")
        }
        
        # Route request to recipient
        recipient_sock = self.controller.get_client_socket(recipient)
        if recipient_sock:
            forward_packet = Packet(ProtocolTypes.FILE_TRANSFER_REQUEST, {
                "file_id": file_id,
                "sender": sender,
                "filename": filename,
                "filesize": filesize
            })
            send_packet(recipient_sock, forward_packet)
        else:
            # Handle offline recipient
            pass

    def handle_transfer_accept(self, client_handler, packet):
        file_id = packet.payload.get("file_id")
        transfer = self.active_transfers.get(file_id)
        
        if transfer and transfer["recipient"] == client_handler.username:
            transfer["status"] = "transferring"
            sender_sock = self.controller.get_client_socket(transfer["sender"])
            if sender_sock:
                send_packet(sender_sock, Packet(ProtocolTypes.FILE_TRANSFER_ACCEPT, {"file_id": file_id}))

    def handle_transfer_chunk(self, client_handler, packet):
        file_id = packet.payload.get("file_id")
        data_base64 = packet.payload.get("data")
        transfer = self.active_transfers.get(file_id)
        
        if transfer and transfer["sender"] == client_handler.username:
            # Decode and write to temp file
            chunk_data = base64.b64decode(data_base64)
            with open(transfer["filepath"], "ab") as f:
                f.write(chunk_data)
            
            transfer["received_bytes"] += len(chunk_data)
            
            # Forward chunk to recipient if online
            recipient_sock = self.controller.get_client_socket(transfer["recipient"])
            if recipient_sock:
                # We reuse the same packet structure to stream to recipient
                try:
                    send_packet(recipient_sock, packet)
                except Exception as e:
                    self.controller.logger.error(f"Failed to forward chunk to {transfer['recipient']}: {e}")

    def handle_transfer_complete(self, client_handler, packet):
        file_id = packet.payload.get("file_id")
        transfer = self.active_transfers.get(file_id)
        
        if transfer and transfer["sender"] == client_handler.username:
            transfer["status"] = "completed"
            self.controller.logger.info(f"File transfer complete: {transfer['filename']} ({file_id})")
            
            # Notify recipient
            recipient_sock = self.controller.get_client_socket(transfer["recipient"])
            if recipient_sock:
                send_packet(recipient_sock, packet)
            
            # In a real app, we'd save this to a 'files' collection in MongoDB
            # For now, it stays on disk in server_data/files/
            # del self.active_transfers[file_id]
