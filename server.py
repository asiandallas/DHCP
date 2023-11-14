#!/usr/bin/env python3
import socket
from ipaddress import IPv4Interface
from datetime import datetime, timedelta

# Time operations in python
# isotimestring = datetime.now().isoformat()
# timestamp = datetime.fromisoformat(isotimestring)
# 60secfromnow = timestamp + timedelta(seconds=60)

# Choose a data structure to store your records
records = [] or {} or object

# List containing all available IP addresses as strings
ip_addresses = [ip.exploded for ip in IPv4Interface("192.168.45.0/28").network.hosts()]

# Parse the client messages
def parse_message(message):
    pass


# Calculate response based on message
def dhcp_operation(parsed_message):
    request = ""
    if request == "LIST":
        pass
    elif request == "DISCOVER":
        pass
    elif request == "REQUEST":
        pass
    elif request == "RELEASE":
        pass
    elif request == "RENEW":
        pass


# Start a UDP server
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Avoid TIME_WAIT socket lock [DO NOT REMOVE]
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("", 9000))
print("DHCP Server running...")

try:
    while True:
        message, clientAddress = server.recvfrom(4096)

        parsed_message = parse_message(message)

        response = dhcp_operation(parsed_message)

        server.sendto(response.encode(), clientAddress)
except OSError:
    pass
except KeyboardInterrupt:
    pass

server.close()
