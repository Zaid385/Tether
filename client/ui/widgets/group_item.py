from PySide6.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QWidget, QPushButton)
from PySide6.QtCore import Qt, Signal
from client.ui.widgets.presence_badge import PresenceBadge
from client.ui.widgets.base import WiseInput, WiseCard
from shared.constants.style import ColorTokens, SpacingTokens, TypographyTokens, RadiusTokens

class GroupItem(QFrame):
    clicked = Signal(str) # group_id

    def __init__(self, group_id, name, member_count=0):
        super().__init__()
        self.group_id = group_id
        self.name = name
        self.setObjectName("GroupItem")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(72)
        self.setup_ui(member_count)

    def setup_ui(self, member_count):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SpacingTokens.LG, SpacingTokens.SM, SpacingTokens.LG, SpacingTokens.SM)
        layout.setSpacing(SpacingTokens.MD)
        
        # Avatar
        self.avatar = QFrame()
        self.avatar.setFixedSize(48, 48)
        self.avatar.setStyleSheet(f"background-color: {ColorTokens.INK}; border-radius: 24px;")
        
        avatar_layout = QVBoxLayout(self.avatar)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        avatar_label = QLabel(self.name[0].upper())
        avatar_label.setAlignment(Qt.AlignCenter)
        avatar_label.setStyleSheet(f"font-weight: 900; color: {ColorTokens.PRIMARY}; font-size: 18px;")
        avatar_layout.addWidget(avatar_label)
        layout.addWidget(self.avatar)
        
        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(SpacingTokens.XXS)
        
        self.name_label = QLabel(self.name)
        self.name_label.setStyleSheet(f"font-weight: {TypographyTokens.WEIGHT_SEMIBOLD}; font-size: 16px; color: {ColorTokens.INK};")
        info_layout.addWidget(self.name_label)
        
        self.members_label = QLabel(f"{member_count} members")
        self.members_label.setStyleSheet(f"color: {ColorTokens.MUTE}; font-size: 12px;")
        info_layout.addWidget(self.members_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
        self._apply_style(False)

    def _apply_style(self, selected=False):
        bg = ColorTokens.PRIMARY_PALE if selected else "transparent"
        self.setStyleSheet(f"""
            QFrame#GroupItem {{
                background-color: {bg};
                border-radius: {RadiusTokens.MD}px;
            }}
            QFrame#GroupItem:hover {{
                background-color: {ColorTokens.CANVAS_SOFT};
            }}
        """)

    def mousePressEvent(self, event):
        self.clicked.emit(self.group_id)
        super().mousePressEvent(event)
