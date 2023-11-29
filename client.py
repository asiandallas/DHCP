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


clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Parsing the message
# [0]OFFER [1]A1:30:9B:D3:CE:18 [2]192.168.45.1 [3]2022-02-02T11:42:08.761340
def parse_message(message):
    message_parts = message.split()
    
    return message_parts

# checks whether the MAC address in the message matches the client's MAC address (line 10)
def check_MAC(message_mac):
    if message_mac == MAC:
        return True
    else:
        return False

# checks whether the timestamp is not expired
def check_timestamp(message_time): # message_time is a string
    current_time = datetime.now()
    timestamp = datetime.fromisoformat(message_time)

    if timestamp > current_time:
        return True
    else:
        return False

def menu():
    print("Choose from the following choices: ")
    print("1. Release")
    print("2. Renew")
    print("3. Quit")

    choice = int(input())
    return choice

# Sending DISCOVER 
print("Client: Discovering...")    
message = "DISCOVER " + MAC
clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
try:
    while True:
        # LISTENING FOR RESPONSE
        message, clientAddress = clientSocket.recvfrom(4096)
        parsed_message = parse_message(message.decode())
        print("Client: Message received from server") 

        if parsed_message[0] == "OFFER":
            if check_MAC(parsed_message[1]) and check_timestamp(parsed_message[3]): # mac from message matches client mac and time not expired
                message = "REQUEST " + parsed_message[1] + " " + parsed_message[2] + " " + parsed_message[3]
                print("Client: Sending request...")
                clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
            else:
                print("Client: OFFER, MAC address does not match or time is expired")
                sys.exit()
                clientSocket.close()
        elif parsed_message[0] == "DECLINE": # request was declined, and the client program terminates
            print("Client: Request Denied!")
            sys.exit()
        elif parsed_message[0] == "ACKNOWLEDGE":
            if check_MAC(not parsed_message[1]): # mac from message DOES NOT matches client mac
                print("Acknowledge Denied!")
                sys.exit()
                clientSocket.close()
            else: # matches
                print("Your IP address is: " + parsed_message[2] + " which will expire at " + parsed_message[3])
                client_choice = menu()
                if client_choice == 1: # release
                        print("Client: Releasing IP address " + parsed_message[1])
                        message = "RELEASE " + parsed_message[1] + " " + parsed_message[2] + " " + parsed_message[3]
                        clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
                elif client_choice == 2: # renew
                    print("Client: Renewing...")
                    message = "RENEW " + parsed_message[1] + " " + parsed_message[2] + " " + parsed_message[3]
                    print(message)
                    clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
                else: # quit
                    sys.exit()
        else: # release goes here?
            client_choice = menu()
            while True:
                if client_choice == 1: # release
                        print("Client: Releasing...")
                        message = "RELEASE " + parsed_message[1] + " " + parsed_message[2] + " " + parsed_message[3]
                        clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
                elif client_choice == 2: # renew
                    print("Client: Renewing...")
                    message = "RENEW " + parsed_message[1] + " " + parsed_message[2] + " " + parsed_message[3]
                    print(message)
                    clientSocket.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
                else: # quit
                    sys.exit()
except OSError:
    sys.exit()
except KeyboardInterrupt:
    sys.exit()

server.close()                
