from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, Property, QPropertyAnimation, Signal, QEasingCurve
from shared.constants.style import ColorTokens, RadiusTokens, TypographyTokens, SpacingTokens

class ToastNotification(QFrame):
    closed = Signal(object)

    def __init__(self, title, message, severity="info", duration=5000):
        super().__init__()
        self.setObjectName("Toast")
        self.setFixedWidth(300)
        self.duration = duration
        self.setup_ui(title, message, severity)
        
        # Opacity for fade effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.0)
        
        # Animations
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(300)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)
        
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(300)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out.finished.connect(lambda: self.closed.emit(self))

    def setup_ui(self, title, message, severity):
        bg_color = ColorTokens.CANVAS
        accent_color = ColorTokens.PRIMARY
        
        if severity == "success": accent_color = ColorTokens.POSITIVE
        elif severity == "warning": accent_color = ColorTokens.WARNING
        elif severity == "error": accent_color = ColorTokens.NEGATIVE
        
        self.setStyleSheet(f"""
            QFrame#Toast {{
                background-color: {bg_color};
                border-left: 4px solid {accent_color};
                border-radius: {RadiusTokens.MD}px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        
        header = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-weight: {TypographyTokens.WEIGHT_SEMIBOLD}; font-size: 14px;")
        header.addWidget(title_label)
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(16, 16)
        close_btn.setStyleSheet("background: transparent; border: none; font-size: 18px; font-weight: bold;")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.hide_toast)
        header.addWidget(close_btn)
        
        layout.addLayout(header)
        
        body = QLabel(message)
        body.setWordWrap(True)
        body.setStyleSheet(f"color: {ColorTokens.BODY}; font-size: 12px;")
        layout.addWidget(body)

    def show_toast(self):
        self.fade_in.start()
        if self.duration > 0:
            QTimer.singleShot(self.duration, self.hide_toast)

    def hide_toast(self):
        self.fade_out.start()

class NotificationManager(QWidget):
    """Container for stacking toasts in the bottom right corner."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignBottom | Qt.AlignRight)
        self.layout.setSpacing(10)
        self.toasts = []

    def notify(self, title, message, severity="info"):
        toast = ToastNotification(title, message, severity)
        toast.closed.connect(self._on_toast_closed)
        self.layout.addWidget(toast)
        toast.show_toast()
        self.toasts.append(toast)
        self._adjust_geometry()

    def _on_toast_closed(self, toast):
        self.layout.removeWidget(toast)
        self.toasts.remove(toast)
        toast.deleteLater()
        self._adjust_geometry()

    def _adjust_geometry(self):
        if self.parent():
            p = self.parent().rect()
            self.setGeometry(p.width() - 320, p.height() - (len(self.toasts) * 100) - 20, 300, len(self.toasts) * 100)
            self.raise_()
