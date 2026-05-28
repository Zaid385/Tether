import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PySide6.QtCore import Qt, QTimer
from client.ui.login_screen import LoginScreen, RegisterScreen
from client.ui.main_chat_window import MainChatWindow
from client.ui.widgets.group_creation_dialog import GroupCreationDialog
from client.ui.widgets.notification_manager import NotificationManager
from client.network.network_manager import NetworkManager
from client.network.typing_manager import TypingStateManager
from client.network.file_manager import FileTransferStateManager
from client.themes.wise_theme import WiseTheme
from shared.protocol.packet import Packet
from shared.constants.network import ProtocolTypes

class TetherClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tether")
        self.resize(1100, 800)
        self.current_user = None
        
        self.network = NetworkManager()
        self.network.packet_received.connect(self.handle_packet)
        self.network.connection_lost.connect(self.on_connection_lost)
        
        # Managers
        self.typing_manager = TypingStateManager()
        self.typing_manager.state_changed.connect(self._send_typing_packet)
        self.file_manager = FileTransferStateManager(self.network)
        self.file_manager.progress_updated.connect(self._update_file_progress)
        self.file_manager.transfer_completed.connect(self._on_file_complete)
        
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        
        # Screens
        self.login_screen = LoginScreen()
        self.login_screen.login_requested.connect(self.login)
        self.login_screen.go_to_register.connect(lambda: self.central_widget.setCurrentWidget(self.register_screen))
        
        self.register_screen = RegisterScreen()
        self.register_screen.register_requested.connect(self.register)
        self.register_screen.go_to_login.connect(lambda: self.central_widget.setCurrentWidget(self.login_screen))
        
        self.main_window = MainChatWindow()
        self.main_window.message_to_send.connect(self.send_message)
        self.main_window.conversation_requested.connect(self.load_history)
        self.main_window.group_history_requested.connect(self.load_group_history)
        self.main_window.logout_requested.connect(self.logout)
        self.main_window.create_group_requested.connect(self.open_group_creation)
        self.main_window.chat_area.typing_state_changed.connect(lambda: self.typing_manager.on_keystroke())
        self.main_window.chat_area.file_requested.connect(self.on_file_requested)
        self.main_window.sidebar.search_triggered.connect(self.perform_search)
        
        self.central_widget.addWidget(self.login_screen)
        self.central_widget.addWidget(self.register_screen)
        self.central_widget.addWidget(self.main_window)
        
        self.notifications = NotificationManager(self)
        self.notifications.show()
        
        self.setStyleSheet(WiseTheme.get_stylesheet())
        
        if not self.network.connect_to_server():
            QMessageBox.critical(self, "Connection Error", "Could not connect to the server.")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(50, self.notifications._adjust_geometry)

    def _ensure_connection(self):
        if not self.network.running: return self.network.connect_to_server()
        return True

    def _send_typing_packet(self, is_typing):
        recipient = self.main_window.current_recipient
        if not recipient or self.main_window.active_is_group: return
        p_type = ProtocolTypes.TYPING_START if is_typing else ProtocolTypes.TYPING_STOP
        self.network.send(Packet(p_type, {"recipient": recipient}))

    def login(self, username, password):
        if not username or not password:
            self.login_screen.login_btn.set_loading(False)
            return
        if not self._ensure_connection():
            self.login_screen.login_btn.set_loading(False)
            return
        self.current_user = username
        self.network.send(Packet(ProtocolTypes.AUTH_LOGIN, {"username": username, "password": password}))

    def register(self, username, password, phone):
        if not username or not password or not phone:
            self.register_screen.register_btn.set_loading(False)
            return
        if not self._ensure_connection():
            self.register_screen.register_btn.set_loading(False)
            return
        self.network.send(Packet(ProtocolTypes.AUTH_REGISTER, {"username": username, "password": password, "phone": phone}))

    def open_group_creation(self):
        contacts = list(self.main_window.sidebar.contacts.keys())
        dialog = GroupCreationDialog(contacts, self)
        if dialog.exec():
            self.network.send(Packet(ProtocolTypes.CREATE_GROUP, {
                "group_name": dialog.name_input.text(),
                "members": dialog.selected_members
            }))

    def perform_search(self, term):
        self.network.send(Packet(ProtocolTypes.SEARCH_REQUEST, {"term": term}))

    def on_file_requested(self, file_path):
        recipient = self.main_window.current_recipient
        if not recipient: return
        filename = os.path.basename(file_path)
        filesize = os.path.getsize(file_path)
        self._pending_upload_path = file_path
        self.network.send(Packet(ProtocolTypes.FILE_TRANSFER_REQUEST, {"recipient": recipient, "filename": filename, "filesize": filesize}))

    def _update_file_progress(self, file_id, percentage):
        if file_id in self.main_window.chat_area.bubbles:
            self.main_window.chat_area.bubbles[file_id].update_progress(percentage)

    def _on_file_complete(self, file_id):
        # If it was a download, it's now saved. We can update preview.
        if file_id in self.file_manager.active_downloads:
            path = self.file_manager.active_downloads[file_id]["path"]
            if file_id in self.main_window.chat_area.bubbles:
                self.main_window.chat_area.bubbles[file_id].set_file_path(path)

    def send_message(self, recipient, text):
        self.typing_manager.stop_typing()
        import uuid
        from datetime import datetime
        m_id = str(uuid.uuid4())
        self.main_window.chat_area.add_message(text, is_mine=True, timestamp=datetime.now().strftime("%I:%M %p"), status="SENT", message_id=m_id)
        
        p_type = ProtocolTypes.GROUP_MESSAGE if self.main_window.active_is_group else ProtocolTypes.MSG_PRIVATE
        payload = {"message_id": m_id, "text": text}
        if self.main_window.active_is_group: payload["group_id"] = recipient
        else: payload["recipient"] = recipient
        self.network.send(Packet(p_type, payload))

    def load_history(self, contact):
        self.network.send(Packet(ProtocolTypes.LOAD_CONVERSATION, {"contact": contact}))

    def load_group_history(self, group_id):
        self.network.send(Packet(ProtocolTypes.GROUP_HISTORY, {"group_id": group_id}))

    def logout(self):
        self.network.send(Packet(ProtocolTypes.PRESENCE_UPDATE, {"status": "offline"}))
        self.main_window.sidebar.clear_all()
        self.main_window.chat_area.clear_messages()
        self.current_user = None
        self.central_widget.setCurrentWidget(self.login_screen)

    def on_login_success(self):
        self.login_screen.login_btn.set_loading(False)
        self.register_screen.register_btn.set_loading(False)
        self.central_widget.setCurrentWidget(self.main_window)
        self.network.send(Packet(ProtocolTypes.GET_CONTACTS, {}))
        self.notifications.notify("Welcome", f"Logged in as {self.current_user}", "success")

    def handle_packet(self, packet):
        p_type = packet.type
        payload = packet.payload
        
        if p_type == ProtocolTypes.AUTH_RESPONSE:
            if payload.get("success"): self.on_login_success()
            else:
                self.login_screen.login_btn.set_loading(False)
                self.register_screen.register_btn.set_loading(False)
                QMessageBox.warning(self, "Auth Failed", payload.get("message"))
        
        elif p_type == ProtocolTypes.CONTACTS_LIST:
            self.main_window.sidebar.clear_contacts()
            for c in payload.get("contacts", []):
                self.main_window.sidebar.add_contact(c["username"], c["status"], c.get("last_message", ""), c.get("unread_count", 0))

        elif p_type == ProtocolTypes.SEARCH_RESULTS:
            self.main_window.sidebar.display_search_results(payload.get("users", []), payload.get("groups", []), payload.get("messages", []))

        elif p_type == ProtocolTypes.GROUP_CREATED:
            g_id = payload.get("group_id")
            g_name = payload.get("group_name")
            members = payload.get("members", [])
            self.main_window.sidebar.add_group(g_id, g_name, len(members))
            self.notifications.notify("New Group", f"You were added to {g_name}", "info")

        elif p_type in [ProtocolTypes.MSG_PRIVATE, ProtocolTypes.GROUP_MESSAGE]:
            is_group = (p_type == ProtocolTypes.GROUP_MESSAGE)
            sender = payload.get("sender")
            text = payload.get("text")
            m_id = payload.get("message_id")
            target_id = payload.get("group_id") if is_group else sender
            
            if not is_group:
                self.network.send(Packet(ProtocolTypes.MSG_DELIVERED, {"message_id": m_id, "sender": sender}))

            if self.main_window.current_recipient == target_id:
                self.main_window.chat_area.add_message(text, is_mine=False, timestamp=self._format_ts(payload.get("timestamp")), message_id=m_id)
                if not is_group: self.network.send(Packet(ProtocolTypes.MSG_READ, {"message_id": m_id, "sender": sender}))
            else:
                self.notifications.notify(f"{sender}", text, "info")
                if sender in self.main_window.sidebar.contacts:
                    self.main_window.sidebar.contacts[sender].set_preview(text, unread=True)

        elif p_type == ProtocolTypes.RECEIPT_UPDATE:
            self.main_window.chat_area.update_bubble_status(payload.get("message_id"), payload.get("status"))

        elif p_type == ProtocolTypes.TYPING_START:
            if self.main_window.current_recipient == payload.get("sender"):
                self.main_window.chat_area.typing_indicator.show_typing(payload.get("sender"))

        elif p_type == ProtocolTypes.TYPING_STOP:
            if self.main_window.current_recipient == payload.get("sender"):
                self.main_window.chat_area.typing_indicator.hide_typing()

        elif p_type == ProtocolTypes.PRESENCE_UPDATE:
            self.main_window.sidebar.update_contact_status(payload.get("username"), payload.get("status"))
            
        elif p_type == ProtocolTypes.NOTIFICATION:
            self.notifications.notify(payload.get("title"), payload.get("body"), payload.get("severity"))

        elif p_type == ProtocolTypes.FILE_TRANSFER_REQUEST:
            f_id = payload.get("file_id")
            sender = payload.get("sender")
            fname = payload.get("filename")
            fsize = payload.get("filesize")
            if self.main_window.current_recipient == sender:
                self.main_window.chat_area.add_file_bubble(f_id, fname, fsize, is_mine=False)
                self.file_manager.start_download(f_id, fname, fsize)
                self.network.send(Packet(ProtocolTypes.FILE_TRANSFER_ACCEPT, {"file_id": f_id}))
            else:
                self.notifications.notify("File Request", f"{sender}: {fname}", "info")

        elif p_type == ProtocolTypes.FILE_TRANSFER_ACCEPT:
            f_id = payload.get("file_id")
            if hasattr(self, '_pending_upload_path'):
                fname = os.path.basename(self._pending_upload_path)
                fsize = os.path.getsize(self._pending_upload_path)
                self.main_window.chat_area.add_file_bubble(f_id, fname, fsize, is_mine=True, file_path=self._pending_upload_path)
                self.file_manager.start_upload(f_id, self._pending_upload_path, self.main_window.current_recipient)
                del self._pending_upload_path

        elif p_type == ProtocolTypes.FILE_TRANSFER_CHUNK:
            self.file_manager.handle_download_chunk(payload.get("file_id"), payload.get("data"))

        elif p_type == ProtocolTypes.FILE_TRANSFER_COMPLETE:
            f_id = payload.get("file_id")
            self.file_manager.finalize_download(f_id)
            self.notifications.notify("File Received", "Download complete", "success")

        elif p_type == ProtocolTypes.CONVERSATION_HISTORY:
            if self.main_window.current_recipient == payload.get("contact"):
                self.main_window.chat_area.clear_messages()
                for msg in payload.get("messages", []):
                    is_mine = (msg["sender"] == self.current_user)
                    self.main_window.chat_area.add_message(msg["text"], is_mine=is_mine, timestamp=self._format_ts(msg["timestamp"]),
                                                        status=msg.get("status", "SENT"), message_id=msg.get("message_id"))
                self.main_window.chat_area.scroll_to_bottom()

        elif p_type == ProtocolTypes.GROUP_HISTORY:
            if self.main_window.current_recipient == payload.get("group_id"):
                self.main_window.chat_area.clear_messages()
                for msg in payload.get("messages", []):
                    is_mine = (msg["sender"] == self.current_user)
                    self.main_window.chat_area.add_message(msg["text"], is_mine=is_mine, timestamp=self._format_ts(msg["timestamp"]),
                                                        status="SENT", message_id=msg.get("message_id"))
                self.main_window.chat_area.scroll_to_bottom()

    def _format_ts(self, iso_ts):
        if not iso_ts: return None
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(iso_ts)
            return dt.strftime("%I:%M %p")
        except: return iso_ts

    def on_connection_lost(self):
        QMessageBox.warning(self, "Connection Error", "Disconnected from server.")
        self.central_widget.setCurrentWidget(self.login_screen)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = TetherClient()
    client.show()
    sys.exit(app.exec())
