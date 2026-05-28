import os
import base64
from PySide6.QtCore import QObject, Signal, QThread
from shared.protocol.packet import Packet
from shared.constants.network import ProtocolTypes

class FileTransferStateManager(QObject):
    """Tracks active uploads and downloads on the client."""
    progress_updated = Signal(str, int) # file_id, percentage
    transfer_completed = Signal(str)
    transfer_failed = Signal(str, str)

    def __init__(self, network_manager):
        super().__init__()
        self.network = network_manager
        self.active_uploads = {} # {file_id: {path, size, sent_bytes}}
        self.active_downloads = {} # {file_id: {path, size, received_bytes}}
        self.chunk_size = 16384 # 16KB chunks
        
        self.download_dir = os.path.join(os.getcwd(), "downloads")
        os.makedirs(self.download_dir, exist_ok=True)

    def start_upload(self, file_id, file_path, recipient):
        file_size = os.path.getsize(file_path)
        self.active_uploads[file_id] = {
            "path": file_path,
            "size": file_size,
            "sent_bytes": 0,
            "recipient": recipient
        }
        self._send_next_chunk(file_id)

    def _send_next_chunk(self, file_id):
        upload = self.active_uploads.get(file_id)
        if not upload: return

        with open(upload["path"], "rb") as f:
            f.seek(upload["sent_bytes"])
            chunk = f.read(self.chunk_size)

        if not chunk:
            # Transfer complete
            self.network.send(Packet(ProtocolTypes.FILE_TRANSFER_COMPLETE, {"file_id": file_id}))
            self.transfer_completed.emit(file_id)
            del self.active_uploads[file_id]
            return

        # Encode chunk to base64 for JSON transport
        encoded_chunk = base64.b64encode(chunk).decode('utf-8')
        
        self.network.send(Packet(ProtocolTypes.FILE_TRANSFER_CHUNK, {
            "file_id": file_id,
            "data": encoded_chunk
        }))
        
        upload["sent_bytes"] += len(chunk)
        percentage = int((upload["sent_bytes"] / upload["size"]) * 100)
        self.progress_updated.emit(file_id, percentage)

    def start_download(self, file_id, filename, filesize):
        file_path = os.path.join(self.download_dir, filename)
        # Avoid overwriting
        counter = 1
        base, ext = os.path.splitext(filename)
        while os.path.exists(file_path):
            file_path = os.path.join(self.download_dir, f"{base}_{counter}{ext}")
            counter += 1
            
        self.active_downloads[file_id] = {
            "path": file_path,
            "size": filesize,
            "received_bytes": 0
        }
        
        # Clear/Create file
        with open(file_path, "wb") as f: pass

    def handle_download_chunk(self, file_id, data_base64):
        download = self.active_downloads.get(file_id)
        if not download: return

        chunk_data = base64.b64decode(data_base64)
        with open(download["path"], "ab") as f:
            f.write(chunk_data)
            
        download["received_bytes"] += len(chunk_data)
        percentage = int((download["received_bytes"] / download["size"]) * 100)
        self.progress_updated.emit(file_id, percentage)

    def finalize_download(self, file_id):
        if file_id in self.active_downloads:
            self.transfer_completed.emit(file_id)
            del self.active_downloads[file_id]
