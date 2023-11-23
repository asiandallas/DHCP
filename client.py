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

# [0]OFFER [1]A1:30:9B:D3:CE:18 [2]192.168.45.1 [3]2022-02-02T11:42:08.761340

# Parse the client messages - gets response  
def parse_message(message):
    response = message.split(' ', 1)[0]
    return response

# Parse the client messages - gets MAC  
def get_MAC(message):
    response = message.split(' ', 1)[1]
    return response

# Parse the client messages - gets IP  
def get_IP(message):
    response = message.split(' ', 1)[2]
    return response

# Parse the client messages - gets timestamp  
def get_time(message):
    response = message.split(' ', 1)[3]
    return response

def menu():
    print("Choose from the following choices: ")
    print("1. Release")
    print("2. Renew")
    print("3. Quit")

    choice = int(input())
    return choice

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    while True:
        # Sending DISCOVER message
        print("Client: Discovering...")    
        message = "DISCOVER " + MAC
        clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
        
        # LISTENING FOR RESPONSE 
        message, clientAddress = socket.recvfrom(4096) 

        # splitting the response into 3 parts
        parsed_message = parse_message(message) 
        response_MAC = get_MAC(message)
        response_IP = get_IP(message)
        response_time = get_time(message)
        timestamp = datetime.fromisoformat(response_time)
        
        if parsed_message == "OFFER":
            if response_MAC == MAC:
                pass
            else:
                print("Client: Requesting " + response_IP + " IP address")
                message = "REQUEST " + MAC + " " + response_IP + " " + response_time
                clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
        elif parsed_message == "DECLINE":
            print("Request Denied!")
            sys.exit()
        elif parsed_message == "ACKNOWLEDGE":
            if response_MAC != MAC:
                print("Acknowledge Denied!")
                sys.exit()
            else:
                print("Your IP address is: " + response_IP + " which will expire at " + response_time)
                client_choice = menu()
                if client_choice == 1: # release
                    message = "RELEASE " + MAC + " " + response_IP + " " + response_time
                    clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
                elif client_choice == 2: # renew
                    message = "RENEW " + MAC + " " + response_IP + " " + response_time
                    clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
                else: # quit
                    clientSocket.close()
                    sys.exit()
except OSError:
    print("OS Error")
    clientSocket.close()
    sys.exit()
except KeyboardInterrupt:
    print("Closing connection and terminating...")
    clientSocket.close()
    sys.exit()
  
clientSocket.close()