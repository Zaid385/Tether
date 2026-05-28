from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from client.ui.widgets.base import WiseButton, WiseInput, WiseCard
from shared.constants.style import ColorTokens, TypographyTokens, SpacingTokens

class LoginScreen(QWidget):
    login_requested = Signal(str, str)
    go_to_register = Signal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.card = WiseCard()
        self.card.setFixedWidth(400)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(SpacingTokens.XL)
        
        heading = QLabel("Tether")
        heading.setAlignment(Qt.AlignCenter)
        heading.setStyleSheet(f"font-weight: {TypographyTokens.WEIGHT_BLACK}; font-size: {TypographyTokens.SIZE_DISPLAY_MD}px; color: {ColorTokens.INK};")
        card_layout.addWidget(heading)
        
        subheading = QLabel("Sign in to your account")
        subheading.setAlignment(Qt.AlignCenter)
        subheading.setStyleSheet(f"font-weight: {TypographyTokens.WEIGHT_SEMIBOLD}; font-size: {TypographyTokens.SIZE_BODY_MD}px; color: {ColorTokens.BODY};")
        card_layout.addWidget(subheading)
        
        self.username_input = WiseInput(placeholder="Username")
        card_layout.addWidget(self.username_input)
        
        self.password_input = WiseInput(placeholder="Password", is_password=True)
        card_layout.addWidget(self.password_input)
        
        self.login_btn = WiseButton("Log in")
        self.login_btn.clicked.connect(self._on_login)
        card_layout.addWidget(self.login_btn)
        
        footer = QHBoxLayout()
        label = QLabel("New to Tether?")
        label.setStyleSheet(f"color: {ColorTokens.BODY}; font-size: {TypographyTokens.SIZE_BODY_SM}px;")
        
        reg_btn = QPushButton("Create account")
        reg_btn.setStyleSheet(f"background: transparent; color: {ColorTokens.INK}; text-decoration: underline; font-weight: 600; border: none;")
        reg_btn.setCursor(Qt.PointingHandCursor)
        reg_btn.clicked.connect(self.go_to_register.emit)
        
        footer.addStretch()
        footer.addWidget(label)
        footer.addWidget(reg_btn)
        footer.addStretch()
        card_layout.addLayout(footer)
        
        layout.addWidget(self.card)

    def _on_login(self):
        self.login_btn.set_loading(True)
        self.login_requested.emit(self.username_input.text(), self.password_input.text())

class RegisterScreen(QWidget):
    register_requested = Signal(str, str, str) # username, password, phone
    go_to_login = Signal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.card = WiseCard()
        self.card.setFixedWidth(400)
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(SpacingTokens.XL)
        
        heading = QLabel("Join Tether")
        heading.setAlignment(Qt.AlignCenter)
        heading.setStyleSheet(f"font-weight: {TypographyTokens.WEIGHT_BLACK}; font-size: {TypographyTokens.SIZE_DISPLAY_MD}px; color: {ColorTokens.INK};")
        card_layout.addWidget(heading)
        
        self.username_input = WiseInput(placeholder="Username")
        card_layout.addWidget(self.username_input)
        
        self.phone_input = WiseInput(placeholder="Phone Number (e.g. +1234567)")
        card_layout.addWidget(self.phone_input)
        
        self.password_input = WiseInput(placeholder="Password", is_password=True)
        card_layout.addWidget(self.password_input)
        
        self.register_btn = WiseButton("Register")
        self.register_btn.clicked.connect(self._on_register)
        card_layout.addWidget(self.register_btn)
        
        footer = QHBoxLayout()
        label = QLabel("Already have an account?")
        label.setStyleSheet(f"color: {ColorTokens.BODY}; font-size: {TypographyTokens.SIZE_BODY_SM}px;")
        
        login_btn = QPushButton("Log in")
        login_btn.setStyleSheet(f"background: transparent; color: {ColorTokens.INK}; text-decoration: underline; font-weight: 600; border: none;")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.go_to_login.emit)
        
        footer.addStretch()
        footer.addWidget(label)
        footer.addWidget(login_btn)
        footer.addStretch()
        card_layout.addLayout(footer)
        
        layout.addWidget(self.card)

    def _on_register(self):
        self.register_btn.set_loading(True)
        self.register_requested.emit(
            self.username_input.text(), 
            self.password_input.text(),
            self.phone_input.text()
        )
