from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Signal
from client.ui.widgets.sidebar import Sidebar
from client.ui.widgets.chat_area import ChatArea

class MainChatWindow(QWidget):
    message_to_send = Signal(str, str)  # recipient, text
    conversation_requested = Signal(str) # contact_username
    group_history_requested = Signal(str) # group_id
    logout_requested = Signal()
    create_group_requested = Signal()

    def __init__(self):
        super().__init__()
        self.current_recipient = None
        self.active_is_group = False
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.sidebar = Sidebar()
        self.sidebar.logout_requested.connect(self.logout_requested.emit)
        self.sidebar.create_group_requested.connect(self.create_group_requested.emit)
        layout.addWidget(self.sidebar)
        
        self.chat_area = ChatArea()
        layout.addWidget(self.chat_area)
        
        # Connect signals
        self.sidebar.contact_selected.connect(self._on_contact_selected)
        self.sidebar.group_selected.connect(self._on_group_selected)
        self.chat_area.message_sent.connect(self._on_message_sent)

    def _on_contact_selected(self, username):
        self.current_recipient = username
        self.active_is_group = False
        self.chat_area.set_contact(username)
        self.conversation_requested.emit(username)

    def _on_group_selected(self, group_id):
        self.current_recipient = group_id
        self.active_is_group = True
        # Find group name
        group_name = self.sidebar.groups[group_id].name
        self.chat_area.set_contact(group_name) # Visual update
        self.group_history_requested.emit(group_id)

    def _on_message_sent(self, text):
        if self.current_recipient:
            self.message_to_send.emit(self.current_recipient, text)
