from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QCheckBox, QMessageBox
from PySide6.QtCore import Qt
from client.ui.widgets.base import WiseButton, WiseInput, WiseCard
from shared.constants.style import ColorTokens, TypographyTokens, SpacingTokens, RadiusTokens

class GroupCreationDialog(QDialog):
    def __init__(self, contacts, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Group")
        self.setFixedWidth(400)
        self.contacts = contacts # list of usernames
        self.selected_members = []
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(f"background-color: {ColorTokens.CANVAS_SOFT};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        title = QLabel("New Group")
        title.setStyleSheet(f"font-weight: {TypographyTokens.WEIGHT_BLACK}; font-size: 24px;")
        layout.addWidget(title)
        
        self.name_input = WiseInput(placeholder="Group Name")
        layout.addWidget(self.name_input)
        
        layout.addWidget(QLabel("Select Members:"))
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: {ColorTokens.CANVAS};
                border: 1px solid {ColorTokens.INK};
                border-radius: {RadiusTokens.MD}px;
                padding: 8px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 8px;
            }}
            QListWidget::item:selected {{
                background-color: {ColorTokens.PRIMARY_PALE};
                color: {ColorTokens.INK};
            }}
        """)
        
        for contact in self.contacts:
            item = QListWidgetItem(contact)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Unchecked)
            self.list_widget.addItem(item)
            
        layout.addWidget(self.list_widget)
        
        buttons = QHBoxLayout()
        cancel_btn = WiseButton("Cancel", is_primary=False)
        cancel_btn.clicked.connect(self.reject)
        
        self.create_btn = WiseButton("Create")
        self.create_btn.clicked.connect(self._on_create)
        
        buttons.addWidget(cancel_btn)
        buttons.addWidget(self.create_btn)
        layout.addLayout(buttons)

    def _on_create(self):
        self.selected_members = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.Checked:
                self.selected_members.append(item.text())
        
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Input Error", "Please enter a group name.")
            return

        if not self.selected_members:
            QMessageBox.warning(self, "Input Error", "Please select at least one member.")
            return

        self.accept()
