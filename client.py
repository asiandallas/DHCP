#!/usr/bin/env python3
import uuid
import socket
from datetime import datetime
import sys


# Time operations in python
# timestamp = datetime.fromisoformat(isotimestring)

# Extract local MAC address [DO NOT CHANGE]
MAC = ":".join(["{:02x}".format((uuid.getnode() >> ele) & 0xFF) for ele in range(0, 8 * 6, 8)][::-1]).upper()

# SERVER IP AND PORT NUMBER [DO NOT CHANGE VAR NAMES]
SERVER_IP = "10.0.0.100"
SERVER_PORT = 9000

# Parse the client messages - gets MAC 
def parse_message(message):
    response = message.split(' ', 1)[1]
    return response

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Sending DISCOVER message    
message = "DISCOVER " + MAC
clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))

# LISTENING FOR RESPONSE - message is response, rest is client address
message, clientAddress = socket.recvfrom(4096) 

# if message == offer
    # MAC address in message == client's MAC address
        # yes - check if time stamp is expired
        # no - send request message containing client's MAC, IP, and timestamp offered by server
# if message == decline
    # display declined message, program terminates
# if message == acknowledge

#current_time = datetime.timestamp(datetime.now())
#timestamp = datetime.fromisoformat(current_time)
parsed_message = parse_message(message)

if message == "OFFER":
     if clientAddress == MAC:
         pass
     else:
         # Sending REQUEST message
         message = "REQUEST " + MAC + " " + IP + " " + timeStamp
elif message == "DECLINE":
    print("Request Denied!")
    clientSocket.close()
    sys.exit()



# Sending REQUEST message

# Sending RELEASE message

# Sending RENEW message

# Can receive decline, offer, acknowledge and list all records from server