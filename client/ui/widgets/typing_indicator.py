from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QTimer
from shared.constants.style import ColorTokens, TypographyTokens

class TypingIndicator(QLabel):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setStyleSheet(f"font-size: {TypographyTokens.SIZE_BODY_SM}px; color: {ColorTokens.POSITIVE}; font-style: italic;")
        self.hide()
        
        self.typing_user = None
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate)
        self.dot_count = 0

    def show_typing(self, username):
        self.typing_user = username
        self.dot_count = 0
        self.setText(f"{username} is typing")
        self.show()
        self.animation_timer.start(500)

    def hide_typing(self):
        self.animation_timer.stop()
        self.hide()
        self.typing_user = None

    def _animate(self):
        self.dot_count = (self.dot_count + 1) % 4
        dots = "." * self.dot_count
        self.setText(f"{self.typing_user} is typing{dots}")
