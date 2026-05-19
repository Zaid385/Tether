from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from client.ui.widgets.sidebar import Sidebar
from client.ui.widgets.chat_area import ChatArea

class MainChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.sidebar = Sidebar()
        layout.addWidget(self.sidebar)
        
        self.chat_area = ChatArea()
        layout.addWidget(self.chat_area)
        
        # Connect signals
        self.sidebar.contact_selected.connect(self.chat_area.set_contact)
