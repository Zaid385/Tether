from PySide6.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QLabel, QScrollArea, QWidget, QPushButton)
from PySide6.QtCore import Qt, Signal
from client.ui.widgets.contact_item import ContactItem
from client.ui.widgets.group_item import GroupItem
from client.ui.widgets.base import WiseInput
from shared.constants.style import ColorTokens, SpacingTokens, TypographyTokens, RadiusTokens

class Sidebar(QFrame):
    contact_selected = Signal(str)
    group_selected = Signal(str)
    logout_requested = Signal()
    create_group_requested = Signal()
    search_triggered = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.setFixedWidth(320)
        self.contacts = {} # {username: ContactItem}
        self.groups = {}   # {group_id: GroupItem}
        self.is_searching = False
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(f"QFrame#Sidebar {{ background-color: {ColorTokens.CANVAS}; border-right: 1px solid {ColorTokens.CANVAS_SOFT}; }}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        header = QFrame()
        header.setFixedHeight(180)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(SpacingTokens.XL, SpacingTokens.XL, SpacingTokens.XL, SpacingTokens.XL)
        header_layout.setSpacing(SpacingTokens.LG)
        
        top_row = QHBoxLayout()
        title = QLabel("Tether")
        title.setStyleSheet(f"font-weight: {TypographyTokens.WEIGHT_BLACK}; font-size: 24px; color: {ColorTokens.INK};")
        top_row.addWidget(title)
        
        self.logout_btn = QPushButton("Logout")
        self.logout_btn.setStyleSheet(f"background: transparent; color: {ColorTokens.NEGATIVE}; font-weight: 600; border: none; text-decoration: underline;")
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.clicked.connect(self.logout_requested.emit)
        top_row.addWidget(self.logout_btn, 0, Qt.AlignRight)
        header_layout.addLayout(top_row)
        
        self.search_input = WiseInput(placeholder="Search...")
        self.search_input.setFixedHeight(40)
        self.search_input.textChanged.connect(self._on_search_changed)
        header_layout.addWidget(self.search_input)
        
        btn_layout = QHBoxLayout()
        self.create_group_btn = QPushButton("+ New Group")
        self.create_group_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ColorTokens.PRIMARY_PALE};
                color: {ColorTokens.INK};
                border-radius: {RadiusTokens.MD}px;
                font-weight: 600;
                padding: 6px;
                border: none;
            }}
            QPushButton:hover {{ background-color: {ColorTokens.PRIMARY_NEUTRAL}; }}
        """)
        self.create_group_btn.setCursor(Qt.PointingHandCursor)
        self.create_group_btn.clicked.connect(self.create_group_requested.emit)
        btn_layout.addWidget(self.create_group_btn)
        header_layout.addLayout(btn_layout)
        layout.addWidget(header)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
        self.main_layout = QVBoxLayout(self.scroll_content)
        self.main_layout.setContentsMargins(SpacingTokens.SM, 0, SpacingTokens.SM, 0)
        self.main_layout.setSpacing(SpacingTokens.XXS)
        
        # Results Section
        self.results_section = self._create_section_label("SEARCH RESULTS")
        self.results_section.hide()
        self.main_layout.addWidget(self.results_section)
        self.search_results_layout = QVBoxLayout()
        self.main_layout.addLayout(self.search_results_layout)

        # Normal Sections
        self.groups_section = self._create_section_label("GROUPS")
        self.main_layout.addWidget(self.groups_section)
        self.groups_layout = QVBoxLayout()
        self.main_layout.addLayout(self.groups_layout)
        
        self.people_section = self._create_section_label("PEOPLE")
        self.main_layout.addWidget(self.people_section)
        self.contacts_layout = QVBoxLayout()
        self.main_layout.addLayout(self.contacts_layout)
        self.main_layout.addStretch()
        
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)

    def _create_section_label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {ColorTokens.MUTE}; font-size: 10px; font-weight: 800; padding: 10px 10px 5px 10px;")
        return lbl

    def add_contact(self, username, status="offline", last_message="", unread_count=0):
        if username in self.contacts:
            item = self.contacts[username]
            item.update_status(status)
            if last_message: item.set_preview(last_message, unread=False)
            return
        item = ContactItem(username, status)
        item.clicked.connect(self._on_contact_clicked)
        if last_message: item.preview_label.setText(last_message)
        if unread_count > 0:
            item.unread_count = unread_count - 1
            item.set_preview(last_message or status, unread=True)
        self.contacts[username] = item
        self.contacts_layout.addWidget(item)

    def add_group(self, group_id, name, member_count=0):
        if group_id in self.groups: return
        item = GroupItem(group_id, name, member_count)
        item.clicked.connect(self._on_group_clicked)
        self.groups[group_id] = item
        self.groups_layout.addWidget(item)

    def _on_search_changed(self, text):
        term = text.strip()
        if len(term) > 2:
            self.is_searching = True
            self.search_triggered.emit(term)
        elif len(term) == 0:
            self.is_searching = False
            self.clear_search_results()

    def display_search_results(self, users, groups, messages):
        self.clear_search_results(only_layout=True)
        if not self.is_searching: return
        
        self.results_section.show()
        self.groups_section.hide()
        self.people_section.hide()
        
        # Display Message results as special items
        for msg in messages:
            item = ContactItem(f"Msg: {msg['sender']}", "online")
            item.set_preview(msg['text'])
            item.clicked.connect(lambda u=msg['sender']: self.contact_selected.emit(u))
            self.search_results_layout.addWidget(item)

    def clear_search_results(self, only_layout=False):
        if not only_layout:
            self.results_section.hide()
            self.groups_section.show()
            self.people_section.show()
        while self.search_results_layout.count():
            child = self.search_results_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()

    def update_contact_status(self, username, status):
        if username in self.contacts: self.contacts[username].update_status(status)

    def _on_contact_clicked(self, username):
        self._clear_selections()
        self.contacts[username]._apply_style(True)
        self.contacts[username].mark_read()
        self.contact_selected.emit(username)

    def _on_group_clicked(self, group_id):
        self._clear_selections()
        self.groups[group_id]._apply_style(True)
        self.group_selected.emit(group_id)

    def _clear_selections(self):
        for item in list(self.contacts.values()) + list(self.groups.values()):
            item._apply_style(False)

    def clear_all(self):
        for item in list(self.contacts.values()) + list(self.groups.values()):
            item.deleteLater()
        self.contacts.clear()
        self.groups.clear()
        
    def clear_contacts(self):
        for item in self.contacts.values(): item.deleteLater()
        self.contacts.clear()
