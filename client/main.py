import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PySide6.QtCore import Qt
from client.ui.login_screen import LoginScreen
from client.network.network_manager import NetworkManager
from client.themes.wise_theme import WiseTheme
from client.ui.login_screen import LoginScreen
from client.ui.main_chat_window import MainChatWindow
from client.network.network_manager import NetworkManager

class TetherClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tether")
        self.resize(1100, 800)

        self.network = NetworkManager()
        self.network.packet_received.connect(self.handle_packet)
        self.network.connection_lost.connect(self.on_connection_lost)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.login_screen = LoginScreen()
        self.login_screen.login_requested.connect(self.login)
        self.login_screen.register_requested.connect(self.register)
        self.central_widget.addWidget(self.login_screen)

        self.main_window = MainChatWindow()
        self.central_widget.addWidget(self.main_window)

        self.setStyleSheet(WiseTheme.get_stylesheet())

        if not self.network.connect_to_server():
            QMessageBox.critical(self, "Connection Error", "Could not connect to the server.")

    def login(self, username, password):
        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password.")
            return

        packet = Packet(ProtocolTypes.AUTH_LOGIN, {
            "username": username,
            "password": password
        })
        self.network.send(packet)

    def register(self, username, password):
        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password.")
            return

        packet = Packet(ProtocolTypes.AUTH_REGISTER, {
            "username": username,
            "password": password
        })
        self.network.send(packet)

    def handle_packet(self, packet):
        if packet.type == ProtocolTypes.AUTH_RESPONSE:
            if packet.payload.get("success"):
                self.on_login_success()
            else:
                QMessageBox.warning(self, "Auth Failed", packet.payload.get("message"))

    def on_login_success(self):
        self.central_widget.setCurrentWidget(self.main_window)
        # For testing, add a few contacts
        self.main_window.sidebar.add_contact("Zaid", "online")
        self.main_window.sidebar.add_contact("System", "online")


    def on_connection_lost(self):
        QMessageBox.warning(self, "Connection Lost", "Disconnected from server.")
        self.central_widget.setCurrentWidget(self.login_screen)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = TetherClient()
    client.show()
    sys.exit(app.exec())
