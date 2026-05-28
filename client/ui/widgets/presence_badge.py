from PySide6.QtWidgets import QFrame, QVBoxLayout
from shared.constants.style import ColorTokens

class PresenceBadge(QFrame):
    def __init__(self, status="offline", size=12):
        super().__init__()
        self.setFixedSize(size, size)
        self.status = status
        self.radius = size // 2
        self.update_status(status)

    def update_status(self, status):
        self.status = status
        color = ColorTokens.MUTE
        if status == "online":
            color = ColorTokens.POSITIVE
        elif status == "away":
            color = ColorTokens.WARNING
            
        self.setStyleSheet(f"""
            background-color: {color};
            border: 2px solid {ColorTokens.CANVAS};
            border-radius: {self.radius}px;
        """)
