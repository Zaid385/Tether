import socket
import threading
from PySide6.QtCore import QObject, Signal
from shared.utils.network_utils import send_packet, receive_packet
from shared.constants.network import NetworkConstants

class NetworkManager(QObject):
    packet_received = Signal(object)  # Emits Packet object
    connection_lost = Signal()
    connected = Signal()

    def __init__(self, host=NetworkConstants.DEFAULT_HOST, port=NetworkConstants.DEFAULT_PORT):
        super().__init__()
        self.host = host
        self.port = port
        self.sock = None
        self.running = False
        self.receive_thread = None

    def connect_to_server(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.running = True
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            self.connected.emit()
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def send(self, packet):
        if self.sock and self.running:
            try:
                send_packet(self.sock, packet)
            except Exception as e:
                print(f"Send error: {e}")
                self.disconnect()

    def _receive_loop(self):
        while self.running:
            try:
                packet = receive_packet(self.sock)
                if packet:
                    self.packet_received.emit(packet)
                else:
                    self.disconnect()
                    break
            except Exception as e:
                print(f"Receive loop error: {e}")
                self.disconnect()
                break

    def disconnect(self):
        self.running = False
        if self.sock:
            self.sock.close()
        self.connection_lost.emit()
