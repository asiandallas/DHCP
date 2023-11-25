#!/usr/bin/env python3
import socket
from ipaddress import IPv4Interface
from datetime import datetime, timedelta

# Time operations in python
# isotimestring = datetime.now().isoformat()
# timestamp = datetime.fromisoformat(isotimestring)
# 60secfromnow = timestamp + timedelta(seconds=60)

# Choose a data structure to store your records
records = {}

# List containing all available IP addresses as strings
ip_addresses = [ip.exploded for ip in IPv4Interface("192.168.45.0/28").network.hosts()]

record_num = 0;

 # Checks if the MAC address in message exists in the records
def mac_exists(mac_address):
    if mac_address in records:
        return True
    else:
        return False
    
def ip_exists(ip):
    if ip in ip_addresses:
        return True
    else:
        return False

# [0]OFFER [1]A1:30:9B:D3:CE:18 [2]192.168.45.1 [3]2022-02-02T11:42:08.761340
# Parse the client messages - gets response  
def parse_message(message):
    message_parts = message.decode().split()
    mac = message_parts[1]
 
    if message_parts[0] != "DISCOVER":
        ip = message_parts[2]
        time = message_parts[3]
    
     # Dictionary and appending it to records
     # mac is the key value
    new_record = {
        "RecordNumber": record_num + 1,
        "MACAddress": mac,
        "IPAddress": ip,
        "Timestamp": time,
        "Acked": False
    }
    records[mac] = new_record
    return message_parts

# Calculate response based on message
def dhcp_operation(parsed_message):
    request = parsed_message[0]
    mac = parsed_message[1]
 
    if parsed_message[0] != "DISCOVER":
        ip = parsed_message[2]
        time = parsed_message[3]

    current_time = datetime.now()

    if request == "LIST":
        pass
    elif request == "DISCOVER":
        if mac_exists(mac):  # MAC address has been assigned
            if records[mac].Timestamp > current_time: # not expired yet
                records[mac].Ackend = True   
                return "ACKNOWLEDGE " + records[mac].MACAddress + " " + records[mac].IPAddress + " " + records[mac].Timestamp
            else: # expired
                isotimestring = datetime.now().isoformat()
                timestamp = datetime.fromisoformat(isotimestring)
                new_time = timestamp + timedelta(seconds=60)
                records[mac].Timestamp = new_time
                records[mac].Ackend = False  
                return "OFFER " + records[mac].MACAddress + " " + records[mac].IPAddress + " " + records[mac].Timestamp
        else: # no IP address has been found
            if ip_exists(ip): # whole list of IP is occupied
                return "DECLINE"
            else:
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
        parsed_message = parse_message(message) # parsed_message stores message_parts
        response = dhcp_operation(parsed_message)
        server.sendto(response.encode(), clientAddress)
except OSError:
    pass
except KeyboardInterrupt:
    pass
  
server.close()
