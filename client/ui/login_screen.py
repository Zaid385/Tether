import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, 
                             QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from client.themes.wise_theme import WiseTheme

class LoginScreen(QWidget):
    login_requested = Signal(str, str)
    register_requested = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        # Card container
        card = QFrame()
        card.setObjectName("Card")
        card.setFixedWidth(400)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(24)
        
        # Heading
        heading = QLabel("Tether")
        heading.setObjectName("Heading")
        heading.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(heading)
        
        subheading = QLabel("Welcome back. Sign in to continue.")
        subheading.setObjectName("SubHeading")
        subheading.setAlignment(Qt.AlignCenter)
        subheading.setWordWrap(True)
        card_layout.addWidget(subheading)
        
        # Inputs
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        card_layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        card_layout.addWidget(self.password_input)
        
        # Buttons
        self.login_btn = QPushButton("Log in")
        self.login_btn.clicked.connect(self._on_login)
        card_layout.addWidget(self.login_btn)
        
        register_container = QHBoxLayout()
        register_label = QLabel("Don't have an account?")
        register_label.setStyleSheet(f"color: {WiseTheme.BODY};")
        self.register_btn = QPushButton("Register")
        self.register_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {WiseTheme.INK};
                text-decoration: underline;
                padding: 0px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                color: {WiseTheme.PRIMARY};
            }}
        """)
        self.register_btn.clicked.connect(self._on_register)
        
        register_container.addStretch()
        register_container.addWidget(register_label)
        register_container.addWidget(self.register_btn)
        register_container.addStretch()
        card_layout.addLayout(register_container)
        
        layout.addWidget(card)

    def _on_login(self):
        self.login_requested.emit(self.username_input.text(), self.password_input.text())

    def _on_register(self):
        self.register_requested.emit(self.username_input.text(), self.password_input.text())
