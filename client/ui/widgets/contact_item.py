from PySide6.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QWidget, QPushButton)
from PySide6.QtCore import Qt, Signal
from client.ui.widgets.presence_badge import PresenceBadge
from client.ui.widgets.base import WiseInput
from shared.constants.style import ColorTokens, SpacingTokens, TypographyTokens, RadiusTokens

class ContactItem(QFrame):
    clicked = Signal(str)

    def __init__(self, username, status="offline", last_seen=None):
        super().__init__()
        self.username = username
        self.unread_count = 0
        self.setObjectName("ContactItem")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(72)
        self.setup_ui(status, last_seen)

    def setup_ui(self, status, last_seen):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SpacingTokens.LG, SpacingTokens.SM, SpacingTokens.LG, SpacingTokens.SM)
        layout.setSpacing(SpacingTokens.MD)
        
        # Avatar with Badge
        self.avatar_container = QFrame()
        self.avatar_container.setFixedSize(48, 48)
        self.avatar_container.setStyleSheet(f"background-color: transparent;")
        
        self.avatar_circle = QFrame(self.avatar_container)
        self.avatar_circle.setFixedSize(48, 48)
        self.avatar_circle.setStyleSheet(f"""
            background-color: {ColorTokens.PRIMARY_PALE};
            border-radius: 24px;
        """)
        
        avatar_label = QLabel(self.username[0].upper(), self.avatar_circle)
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setFixedSize(48, 48)
        avatar_label.setStyleSheet(f"font-weight: 900; color: {ColorTokens.INK_DEEP}; font-size: 18px;")
        
        self.badge = PresenceBadge(status, size=14)
        self.badge.setParent(self.avatar_container)
        self.badge.move(34, 34)
        
        layout.addWidget(self.avatar_container)
        
        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(SpacingTokens.XXS)
        
        name_row = QHBoxLayout()
        self.name_label = QLabel(self.username)
        self.name_label.setStyleSheet(f"font-weight: {TypographyTokens.WEIGHT_SEMIBOLD}; font-size: 15px; color: {ColorTokens.INK};")
        name_row.addWidget(self.name_label)
        
        self.unread_badge = QLabel("0")
        self.unread_badge.setFixedSize(18, 18)
        self.unread_badge.setAlignment(Qt.AlignCenter)
        self.unread_badge.setStyleSheet(f"""
            background-color: {ColorTokens.POSITIVE};
            color: white;
            border-radius: 9px;
            font-size: 10px;
            font-weight: bold;
        """)
        self.unread_badge.hide()
        name_row.addStretch()
        name_row.addWidget(self.unread_badge)
        info_layout.addLayout(name_row)
        
        self.preview_label = QLabel(status)
        self.preview_label.setStyleSheet(f"color: {ColorTokens.MUTE}; font-size: 12px;")
        self.preview_label.setFixedWidth(180) # Truncate long messages
        info_layout.addWidget(self.preview_label)
        
        layout.addLayout(info_layout)
        
        self._apply_style(False)

    def _apply_style(self, selected=False):
        bg = ColorTokens.PRIMARY_PALE if selected else "transparent"
        self.setStyleSheet(f"""
            QFrame#ContactItem {{
                background-color: {bg};
                border-radius: {RadiusTokens.MD}px;
            }}
            QFrame#ContactItem:hover {{
                background-color: {ColorTokens.CANVAS_SOFT};
            }}
        """)

    def update_status(self, status):
        if self.preview_label.text() in ["online", "offline", "away"]:
            self.preview_label.setText(status)
        self.badge.update_status(status)

    def set_preview(self, text, unread=False):
        self.preview_label.setText(text)
        if unread:
            self.unread_count += 1
            self.unread_badge.setText(str(self.unread_count))
            self.unread_badge.show()
            self.name_label.setStyleSheet(f"font-weight: 900; font-size: 15px; color: {ColorTokens.INK};")

    def mark_read(self):
        self.unread_count = 0
        self.unread_badge.hide()
        self.name_label.setStyleSheet(f"font-weight: {TypographyTokens.WEIGHT_SEMIBOLD}; font-size: 15px; color: {ColorTokens.INK};")

    def mousePressEvent(self, event):
        self.mark_read()
        self.clicked.emit(self.username)
        super().mousePressEvent(event)
