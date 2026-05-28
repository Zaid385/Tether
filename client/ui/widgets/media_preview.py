from PySide6.QtWidgets import QLabel, QFrame, QVBoxLayout, QDialog
from PySide6.QtGui import QPixmap, QImage, QCursor
from PySide6.QtCore import Qt, Signal
from shared.constants.style import RadiusTokens

class ImageLightbox(QDialog):
    """A full-screen-ish dialog to view images at full size."""
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Preview")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        self.image_label = QLabel()
        
        # Scale to fit screen but keep aspect ratio
        screen_size = self.screen().size()
        scaled_pixmap = pixmap.scaled(
            screen_size.width() * 0.8, 
            screen_size.height() * 0.8, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setStyleSheet(f"border-radius: {RadiusTokens.LG}px; background: black;")
        self.image_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.image_label)
        self.setFixedSize(self.image_label.sizeHint())

    def mousePressEvent(self, event):
        self.close()

class ImagePreviewWidget(QFrame):
    """A thumbnail widget that expands on click."""
    clicked = Signal(object)

    def __init__(self, image_path, max_width=300, max_height=200):
        super().__init__()
        self.image_path = image_path
        self.setup_ui(max_width, max_height)

    def setup_ui(self, mw, mh):
        self.setCursor(Qt.PointingHandCursor)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.pixmap = QPixmap(self.image_path)
        if self.pixmap.isNull():
            # Placeholder for corrupted/missing images
            self.label = QLabel("📷 Image unavailable")
            self.label.setStyleSheet("color: grey; font-style: italic; padding: 20px;")
        else:
            self.label = QLabel()
            thumbnail = self.pixmap.scaled(mw, mh, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.label.setPixmap(thumbnail)
            self.label.setStyleSheet(f"border-radius: {RadiusTokens.MD}px;")
        
        layout.addWidget(self.label)

    def mousePressEvent(self, event):
        if not self.pixmap.isNull():
            lightbox = ImageLightbox(self.pixmap, self.window())
            lightbox.exec()
        super().mousePressEvent(event)
