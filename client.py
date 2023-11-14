#!/usr/bin/env python3
import uuid
import socket
from datetime import datetime

# Time operations in python
# timestamp = datetime.fromisoformat(isotimestring)

# Extract local MAC address [DO NOT CHANGE]
MAC = ":".join(["{:02x}".format((uuid.getnode() >> ele) & 0xFF) for ele in range(0, 8 * 6, 8)][::-1]).upper()

# SERVER IP AND PORT NUMBER [DO NOT CHANGE VAR NAMES]
SERVER_IP = "10.0.0.100"
SERVER_PORT = 9000


clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Sending DISCOVER message
message = "DISCOVER " + MAC
clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))

# LISTENING FOR RESPONSE
message, _ = socket.recvfrom(4096)
