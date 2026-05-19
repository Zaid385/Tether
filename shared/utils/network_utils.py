import struct
import json
from shared.constants.network import NetworkConstants

def send_packet(sock, packet):
    """Sends a Packet object over a socket with a 4-byte length header."""
    json_data = packet.to_json().encode('utf-8')
    header = struct.pack('>I', len(json_data))
    sock.sendall(header + json_data)

def receive_packet(sock):
    """Receives a Packet object from a socket by reading the 4-byte length header first."""
    header = b""
    while len(header) < NetworkConstants.HEADER_SIZE:
        chunk = sock.recv(NetworkConstants.HEADER_SIZE - len(header))
        if not chunk:
            return None
        header += chunk
    
    payload_length = struct.unpack('>I', header)[0]
    
    payload_data = b""
    while len(payload_data) < payload_length:
        chunk = sock.recv(min(payload_length - len(payload_data), NetworkConstants.BUFFER_SIZE))
        if not chunk:
            return None
        payload_data += chunk
        
    from shared.protocol.packet import Packet
    return Packet.from_json(payload_data.decode('utf-8'))
