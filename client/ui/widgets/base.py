from PySide6.QtWidgets import QPushButton, QLineEdit, QFrame, QTextEdit
from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QTextDocument
from shared.constants.style import ColorTokens, RadiusTokens, TypographyTokens, SpacingTokens

class WiseButton(QPushButton):
    def __init__(self, text, parent=None, is_primary=True):
        super().__init__(text, parent)
        self.is_primary = is_primary
        self.original_text = text
        self.is_loading = False
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self._apply_style()

    def _apply_style(self):
        bg = ColorTokens.PRIMARY if self.is_primary else ColorTokens.CANVAS_SOFT
        hover = ColorTokens.PRIMARY_HOVER if self.is_primary else "#f0f2ef"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {ColorTokens.INK};
                border-radius: {RadiusTokens.XL}px;
                font-weight: {TypographyTokens.WEIGHT_SEMIBOLD};
                font-size: {TypographyTokens.SIZE_BODY_MD}px;
                padding: 0 {SpacingTokens.XL}px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:disabled {{
                background-color: {ColorTokens.MUTE};
                color: {ColorTokens.CANVAS};
            }}
        """)

    def set_loading(self, loading: bool):
        self.is_loading = loading
        if loading:
            self.setEnabled(False)
            self.setText("Please wait...")
        else:
            self.setEnabled(True)
            self.setText(self.original_text)

class WiseInput(QLineEdit):
    def __init__(self, placeholder="", is_password=False, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        if is_password:
            self.setEchoMode(QLineEdit.Password)
        self.setFixedHeight(48)
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {ColorTokens.CANVAS};
                color: {ColorTokens.INK};
                border: 1px solid {ColorTokens.INK};
                border-radius: {RadiusTokens.MD}px;
                padding: 0 {SpacingTokens.LG}px;
                font-size: {TypographyTokens.SIZE_BODY_MD}px;
            }}
            QLineEdit:focus {{
                border: 2px solid {ColorTokens.PRIMARY};
            }}
        """)

class WiseTextArea(QTextEdit):
    """A multi-line text area that expands vertically and handles Shift+Enter."""
    returnPressed = Signal()

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setAcceptRichText(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMinimumHeight(48)
        self.setMaximumHeight(150)
        self._apply_style()
        self.textChanged.connect(self.adjust_height)

    def _apply_style(self):
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {ColorTokens.CANVAS};
                color: {ColorTokens.INK};
                border: 1px solid {ColorTokens.INK};
                border-radius: {RadiusTokens.MD}px;
                padding: 8px {SpacingTokens.LG}px;
                font-size: {TypographyTokens.SIZE_BODY_MD}px;
            }}
            QTextEdit:focus {{
                border: 2px solid {ColorTokens.PRIMARY};
            }}
        """)

    def adjust_height(self):
        doc_height = self.document().size().height()
        new_height = max(48, min(doc_height + 16, 150))
        self.setFixedHeight(int(new_height))
        if new_height >= 150:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if event.modifiers() & Qt.ShiftModifier:
                # Add new line
                super().keyPressEvent(event)
            else:
                # Submit message
                self.returnPressed.emit()
        else:
            super().keyPressEvent(event)

class WiseCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("WiseCard")
        self.setStyleSheet(f"""
            QFrame#WiseCard {{
                background-color: {ColorTokens.CANVAS};
                border-radius: {RadiusTokens.XL}px;
            }}
        """)
