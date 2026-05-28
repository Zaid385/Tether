from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QScrollArea, QFrame, QFileDialog, QProgressBar, QTextEdit)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QTextOption
from client.themes.wise_theme import WiseTheme
from client.ui.widgets.base import WiseButton, WiseInput, WiseTextArea
from shared.constants.style import ColorTokens, RadiusTokens, TypographyTokens, SpacingTokens
from client.ui.widgets.typing_indicator import TypingIndicator
from client.ui.widgets.media_preview import ImagePreviewWidget

class FileTransferBubble(QFrame):
    def __init__(self, filename, filesize, is_mine=True, file_path=None):
        super().__init__()
        self.filename = filename
        self.filesize = filesize
        self.is_mine = is_mine
        self.file_path = file_path
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.bubble = QFrame()
        self.bubble.setFixedWidth(300)
        self.bubble_layout = QVBoxLayout(self.bubble)
        self.bubble_layout.setContentsMargins(16, 12, 16, 12)
        self.bubble_layout.setSpacing(10)
        
        # Check if it's an image and if we have a path
        if self.file_path and self.file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            self.preview = ImagePreviewWidget(self.file_path, max_width=268)
            self.bubble_layout.addWidget(self.preview)
        
        header = QHBoxLayout()
        icon = QLabel("📄")
        icon.setStyleSheet("font-size: 24px;")
        header.addWidget(icon)
        
        info = QVBoxLayout()
        name_lbl = QLabel(self.filename)
        name_lbl.setStyleSheet(f"font-weight: 600; font-size: 13px; color: {ColorTokens.INK};")
        name_lbl.setWordWrap(True)
        info.addWidget(name_lbl)
        
        size_lbl = QLabel(f"{self.filesize / 1024:.1f} KB")
        size_lbl.setStyleSheet(f"font-size: 11px; color: {ColorTokens.MUTE};")
        info.addWidget(size_lbl)
        header.addLayout(info)
        self.bubble_layout.addLayout(header)
        
        self.progress = QProgressBar()
        self.progress.setFixedHeight(4)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet(f"QProgressBar {{ background: {ColorTokens.CANVAS_SOFT}; border: none; border-radius: 2px; }} QProgressBar::chunk {{ background: {ColorTokens.POSITIVE}; border-radius: 2px; }}")
        self.bubble_layout.addWidget(self.progress)
        
        self.status_lbl = QLabel("Uploading..." if self.is_mine else "Waiting...")
        self.status_lbl.setStyleSheet("font-size: 10px; font-style: italic;")
        self.bubble_layout.addWidget(self.status_lbl)
        
        if self.is_mine:
            self.bubble.setStyleSheet(f"background-color: {ColorTokens.PRIMARY_PALE}; border-radius: {RadiusTokens.MD}px; border-top-right-radius: 4px;")
            self.layout.addWidget(self.bubble, 0, Qt.AlignRight)
        else:
            self.bubble.setStyleSheet(f"background-color: {ColorTokens.CANVAS_SOFT}; border-radius: {RadiusTokens.MD}px; border-top-left-radius: 4px;")
            self.layout.addWidget(self.bubble, 0, Qt.AlignLeft)

    def update_progress(self, percentage):
        self.progress.setValue(percentage)
        if percentage >= 100:
            self.status_lbl.setText("Completed")
            self.progress.hide()

    def set_file_path(self, path):
        """Update bubble with a preview if it's an image."""
        self.file_path = path
        if path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            # Add preview to top of bubble
            preview = ImagePreviewWidget(path, max_width=268)
            self.bubble_layout.insertWidget(0, preview)

class MessageBubble(QFrame):
    def __init__(self, text, is_mine=True, timestamp="10:00 AM", status="SENT", message_id=None):
        super().__init__()
        self.message_id = message_id
        self.setup_ui(text, is_mine, timestamp, status)

    def setup_ui(self, text, is_mine, timestamp, status):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        bubble = QFrame()
        bubble.setMinimumWidth(100)
        bubble.setMaximumWidth(450)
        
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(SpacingTokens.LG, SpacingTokens.MD, SpacingTokens.LG, SpacingTokens.MD)
        bubble_layout.setSpacing(SpacingTokens.XS)
        
        self.content = QTextEdit(text)
        self.content.setReadOnly(True)
        self.content.setAcceptRichText(False)
        self.content.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.content.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.content.setFrameStyle(QFrame.NoFrame)
        self.content.setWordWrapMode(QTextOption.WrapAnywhere)
        self.content.setStyleSheet(f"background: transparent; font-size: {TypographyTokens.SIZE_BODY_MD}px; color: {ColorTokens.INK};")
        
        doc = self.content.document()
        doc.setTextWidth(bubble.maximumWidth() - 40)
        self.content.setFixedHeight(int(doc.size().height()) + 10)
        bubble_layout.addWidget(self.content)
        
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(SpacingTokens.SM)
        footer_layout.setAlignment(Qt.AlignRight)
        
        time_label = QLabel(timestamp)
        time_label.setStyleSheet(f"font-size: 11px; color: {ColorTokens.BODY}; font-weight: 600;")
        footer_layout.addWidget(time_label)
        
        if is_mine:
            self.status_label = QLabel()
            self.update_status(status)
            footer_layout.addWidget(self.status_label)
            bubble.setStyleSheet(f"background-color: {ColorTokens.PRIMARY}; border-radius: {RadiusTokens.MD}px; border-top-right-radius: 4px;")
            bubble_layout.addLayout(footer_layout)
            layout.addWidget(bubble, 0, Qt.AlignRight)
        else:
            bubble.setStyleSheet(f"background-color: {ColorTokens.CANVAS_SOFT}; border-radius: {RadiusTokens.MD}px; border-top-left-radius: 4px;")
            bubble_layout.addLayout(footer_layout)
            layout.addWidget(bubble, 0, Qt.AlignLeft)

    def update_status(self, status):
        icon = "✓"
        color = ColorTokens.BODY 
        if status == "DELIVERED": icon = "✓✓"
        elif status == "READ": icon = "✓✓"; color = ColorTokens.INK_DEEP 
        self.status_label.setText(icon)
        self.status_label.setStyleSheet(f"font-size: 16px; font-weight: 900; color: {color}; margin-bottom: -1px;")

class ChatArea(QWidget):
    message_sent = Signal(str)
    file_requested = Signal(str)
    typing_state_changed = Signal(bool)

    def __init__(self):
        super().__init__()
        self.bubbles = {}
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.header = QFrame()
        self.header.setStyleSheet(f"background-color: {ColorTokens.CANVAS}; border-bottom: 1px solid {ColorTokens.CANVAS_SOFT};")
        header_layout = QVBoxLayout(self.header)
        header_layout.setContentsMargins(SpacingTokens.XL, 20, SpacingTokens.XL, 20)
        
        self.chat_title = QLabel("Select a contact")
        self.chat_title.setStyleSheet(f"font-weight: {TypographyTokens.WEIGHT_SEMIBOLD}; font-size: 18px;")
        header_layout.addWidget(self.chat_title)
        
        self.typing_indicator = TypingIndicator()
        header_layout.addWidget(self.typing_indicator)
        self.layout.addWidget(self.header)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet(f"background-color: {ColorTokens.CANVAS};")
        self.messages_layout = QVBoxLayout(self.scroll_content)
        self.messages_layout.setContentsMargins(SpacingTokens.XL, SpacingTokens.XL, SpacingTokens.XL, SpacingTokens.XL)
        self.messages_layout.setSpacing(SpacingTokens.LG)
        self.messages_layout.addStretch()
        self.scroll.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll)
        
        self.input_container = QFrame()
        self.input_container.setStyleSheet(f"background-color: {ColorTokens.CANVAS}; border-top: 1px solid {ColorTokens.CANVAS_SOFT};")
        self.input_layout = QHBoxLayout(self.input_container)
        self.input_layout.setContentsMargins(SpacingTokens.XL, 16, SpacingTokens.XL, 16)
        self.input_layout.setSpacing(SpacingTokens.LG)
        self.input_layout.setAlignment(Qt.AlignBottom)
        
        self.attach_btn = QPushButton("📎")
        self.attach_btn.setFixedSize(40, 48)
        self.attach_btn.setStyleSheet("font-size: 20px; border: none; background: transparent;")
        self.attach_btn.setCursor(Qt.PointingHandCursor)
        self.attach_btn.clicked.connect(self._on_attach)
        self.input_layout.addWidget(self.attach_btn)
        
        self.message_input = WiseTextArea(placeholder="Type a message...")
        self.message_input.returnPressed.connect(self._send_message)
        self.input_layout.addWidget(self.message_input)
        
        self.send_btn = WiseButton("Send")
        self.send_btn.clicked.connect(self._send_message)
        self.input_layout.addWidget(self.send_btn)
        self.layout.addWidget(self.input_container)

    def scroll_to_bottom(self):
        QTimer.singleShot(50, lambda: self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum()))
        QTimer.singleShot(200, lambda: self.scroll.verticalScrollBar().setValue(self.scroll.verticalScrollBar().maximum()))

    def set_contact(self, username):
        self.chat_title.setText(username)
        self.typing_indicator.hide_typing()
        self.clear_messages()

    def clear_messages(self):
        self.bubbles.clear()
        for i in reversed(range(1, self.messages_layout.count())):
            item = self.messages_layout.itemAt(i)
            if item and item.widget(): item.widget().deleteLater()

    def add_message(self, text, is_mine=True, timestamp=None, status="SENT", message_id=None):
        if not timestamp:
            from datetime import datetime
            timestamp = datetime.now().strftime("%I:%M %p")
        bubble = MessageBubble(text, is_mine, timestamp, status, message_id)
        if message_id: self.bubbles[message_id] = bubble
        self.messages_layout.addWidget(bubble)
        self.scroll_to_bottom()

    def add_file_bubble(self, file_id, filename, filesize, is_mine=True, file_path=None):
        bubble = FileTransferBubble(filename, filesize, is_mine, file_path)
        self.bubbles[file_id] = bubble
        self.messages_layout.addWidget(bubble)
        self.scroll_to_bottom()
        return bubble

    def update_bubble_status(self, message_id, status):
        if message_id in self.bubbles and hasattr(self.bubbles[message_id], 'update_status'):
            self.bubbles[message_id].update_status(status)

    def _on_attach(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path: self.file_requested.emit(file_path)

    def _send_message(self):
        text = self.message_input.toPlainText().strip()
        if text:
            self.message_sent.emit(text)
            self.message_input.clear()
            self.message_input.adjust_height()
