from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QScrollArea, QFrame)
from PySide6.QtCore import Qt, Signal
from client.themes.wise_theme import WiseTheme

class MessageBubble(QFrame):
    def __init__(self, text, is_mine=True, timestamp="10:00 AM"):
        super().__init__()
        self.setup_ui(text, is_mine, timestamp)

    def setup_ui(self, text, is_mine, timestamp):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        bubble = QFrame()
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(16, 12, 16, 12)
        
        content = QLabel(text)
        content.setWordWrap(True)
        bubble_layout.addWidget(content)
        
        time_label = QLabel(timestamp)
        time_label.setStyleSheet(f"font-size: 10px; color: {WiseTheme.MUTE};")
        time_label.setAlignment(Qt.AlignRight)
        bubble_layout.addWidget(time_label)
        
        if is_mine:
            bubble.setStyleSheet(f"""
                background-color: {WiseTheme.PRIMARY};
                border-radius: {WiseTheme.RADIUS_MD};
                border-top-right-radius: 4px;
            """)
            layout.addWidget(bubble, 0, Qt.AlignRight)
        else:
            bubble.setStyleSheet(f"""
                background-color: {WiseTheme.CANVAS_SOFT};
                border-radius: {WiseTheme.RADIUS_MD};
                border-top-left-radius: 4px;
            """)
            layout.addWidget(bubble, 0, Qt.AlignLeft)

class ChatArea(QWidget):
    message_sent = Signal(str)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Header
        self.header = QFrame()
        self.header.setFixedHeight(80)
        self.header.setStyleSheet(f"background-color: {WiseTheme.CANVAS}; border-bottom: 1px solid {WiseTheme.CANVAS_SOFT};")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(24, 0, 24, 0)
        
        self.chat_title = QLabel("Select a contact")
        self.chat_title.setStyleSheet("font-weight: 600; font-size: 18px;")
        header_layout.addWidget(self.chat_title)
        
        self.layout.addWidget(self.header)
        
        # Messages scroll area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.messages_layout = QVBoxLayout(self.scroll_content)
        self.messages_layout.setContentsMargins(24, 24, 24, 24)
        self.messages_layout.setSpacing(16)
        self.messages_layout.addStretch()
        
        self.scroll.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll)
        
        # Input area
        input_container = QFrame()
        input_container.setFixedHeight(80)
        input_container.setStyleSheet(f"background-color: {WiseTheme.CANVAS};")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(24, 0, 24, 0)
        input_layout.setSpacing(16)
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type a message...")
        self.message_input.returnPressed.connect(self._send_message)
        input_layout.addWidget(self.message_input)
        
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(send_btn)
        
        self.layout.addWidget(input_container)

    def set_contact(self, username):
        self.chat_title.setText(username)
        # Clear messages (for now)
        for i in reversed(range(self.messages_layout.count())):
            item = self.messages_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        self.messages_layout.addStretch()

    def add_message(self, text, is_mine=True):
        bubble = MessageBubble(text, is_mine)
        # Insert before the stretch
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)
        # Auto scroll to bottom
        self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum())

    def _send_message(self):
        text = self.message_input.text().strip()
        if text:
            self.message_sent.emit(text)
            self.message_input.clear()
