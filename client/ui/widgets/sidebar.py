from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QFrame, QPushButton)
from PySide6.QtCore import Qt, Signal
from client.themes.wise_theme import WiseTheme

class ContactItem(QFrame):
    clicked = Signal(str)  # Emits username

    def __init__(self, username, status="offline"):
        super().__init__()
        self.username = username
        self.setObjectName("ContactItem")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(72)
        self.setup_ui(status)

    def setup_ui(self, status):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)
        
        # Avatar placeholder
        avatar = QFrame()
        avatar.setFixedSize(48, 48)
        avatar.setStyleSheet(f"""
            background-color: {WiseTheme.PRIMARY_PALE};
            border-radius: 24px;
        """)
        avatar_layout = QVBoxLayout(avatar)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        avatar_label = QLabel(self.username[0].upper())
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setStyleSheet(f"font-weight: 900; color: {WiseTheme.INK_DEEP}; font-size: 18px;")
        avatar_layout.addWidget(avatar_label)
        layout.addWidget(avatar)
        
        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        name_label = QLabel(self.username)
        name_label.setStyleSheet("font-weight: 600; font-size: 16px;")
        info_layout.addWidget(name_label)
        
        self.status_label = QLabel(status)
        self.status_label.setStyleSheet(f"color: {WiseTheme.MUTE}; font-size: 12px;")
        info_layout.addWidget(self.status_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()

    def mousePressEvent(self, event):
        self.clicked.emit(self.username)
        super().mousePressEvent(event)

class Sidebar(QFrame):
    contact_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(300)
        self.setStyleSheet(f"background-color: {WiseTheme.CANVAS}; border-right: 1px solid {WiseTheme.CANVAS_SOFT};")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setFixedHeight(80)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 0, 24, 0)
        
        title = QLabel("Messages")
        title.setStyleSheet("font-weight: 900; font-size: 24px;")
        header_layout.addWidget(title)
        
        layout.addWidget(header)
        
        # Scroll area for contacts
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.contacts_layout = QVBoxLayout(self.scroll_content)
        self.contacts_layout.setContentsMargins(8, 8, 8, 8)
        self.contacts_layout.setSpacing(4)
        self.contacts_layout.addStretch()
        
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)

    def add_contact(self, username, status="offline"):
        item = ContactItem(username, status)
        item.clicked.connect(self.contact_selected)
        # Insert before the stretch
        self.contacts_layout.insertWidget(self.contacts_layout.count() - 1, item)
