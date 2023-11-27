#!/usr/bin/env python3
import socket
from ipaddress import IPv4Interface
from datetime import datetime, timedelta
import sys

# Time operations in python
# isotimestring = datetime.now().isoformat()
# timestamp = datetime.fromisoformat(isotimestring)
# 60secfromnow = timestamp + timedelta(seconds=60)

# Choose a data structure to store your records
records = {}

# List containing all available IP addresses as strings
ip_addresses = [ip.exploded for ip in IPv4Interface("192.168.45.0/28").network.hosts()]

# global variable for the record number
record_num = 0

# Parse the client messages
# # [0]OFFER [1]A1:30:9B:D3:CE:18 [2]192.168.45.1 [3]2022-02-02T11:42:08.761340
def parse_message(message):
    message_parts = message.split()
    mac = message_parts[1]

    if (len(message_parts) == 4): # normal case
        # Dictionary and appending it to records
        # mac is the key value
        new_record = {
            "RecordNumber": record_num + 1,
            "MACAddress": message_parts[1],
            "IPAddress": message_parts[2],
            "Timestamp": message_parts[3],
            "Acked": False
        }
        records[mac] = new_record
        return message_parts
    else:
        return message_parts

# Checks if the MAC address in message exists in the records
def mac_exists(mac_address):
    if mac_address in records:
        return True
    else:
        return False

def check_ip(mac):
    for mac, record in records.items():
        if mac in record and 'IPAddress' in record[mac] and record[mac]['IPAddress'] in ip_addresses:
            return True
    return False

# Checks if timestamp is expired
def check_time(mac):
    current_time = datetime.now().isoformat()

    # Loop through the records and check if each timestamp is less than the current time
    for mac_address, record in records.items():
        timestamp = record.get('Timestamp')
        if current_time > timestamp: # expired
            return record
    return -1

def get_nextIP():
    for ip in ip_addresses:
        if ip not in [record['IPAddress'] for record in records.values()]:
            return ip
 
# Calculate response based on message
def dhcp_operation(parsed_message):
    request = parsed_message[0]
    if request == "LIST":
        return json.dumps(client_records)
    elif request == "DISCOVER":
        mac = parsed_message[1]  # Extract the MAC address from the request
        if mac_exists(mac): # record found
            current_time = datetime.now()
            message_time_with_space = records[mac]['Timestamp'][:10] + ' ' + records[mac]['Timestamp'][10:]
            record_time = datetime.fromisoformat(message_time_with_space)

            if record_time > current_time: # not expired yet
                records[mac]['Acked'] = True   
                return f"ACKNOWLEDGE {records[mac]['MACAddress']} {records[mac]['IPAddress']} {records[mac]['Timestamp']}"
            else: # expired
                current_time = datetime.now().isoformat()
                timestamp = datetime.fromisoformat(current_time)
                new_time = timestamp + timedelta(seconds=60)
                records[mac]['Timestamp'] = new_time
                records[mac]['Acked'] = False  
                return f"OFFER {records[mac]['MACAddress']} {records[mac]['IPAddress']} {records[mac]['Timestamp']}"
            
        else: # no record found
            ip_used = check_ip(parsed_message[1]) # returns true if found, false if not
            time_expired = check_time(parsed_message[1]) # returns index of expired time, -1 if none
            if (ip_used == True) and (time_expired != -1): # ip found and something is expired
                records[time_expired]['IPAddress'] = ip_addresses[time_expired]

                current_time = datetime.now().isoformat()
                timestamp = datetime.fromisoformat(current_time)
                new_time = timestamp + timedelta(seconds=60)
                records[time_expired].Timestamp = new_time
                records[mac].Ackend = False
            elif (ip_used == True) and (time_expired == -1): # ip found but none are expired
                return "DECLINE"
            else:
                current_time = datetime.now().isoformat()
                timestamp = datetime.fromisoformat(current_time)
                new_time = timestamp + timedelta(seconds=60)
                # Format the timestamp without space between date and time
                formatted_timestamp = new_time.strftime("%Y-%m-%d%H:%M:%S.%f")
                new_record = {
                    "RecordNumber": record_num + 1,
                    "MACAddress": mac,
                    "IPAddress": get_nextIP(),
                    "Timestamp": formatted_timestamp,
                    "Acked": False
                }
                records[mac] = new_record
                print(records[mac]['Timestamp'])
                return f"OFFER {records[mac]['MACAddress']} {records[mac]['IPAddress']} {records[mac]['Timestamp']}"
            
    elif request == "REQUEST":
        mac = parsed_message[1]  # Extract the MAC address from the request
        ip = parsed_message[2]  # Extract the requested IP from the request
        timestamp = parsed_message[3]  # Extract the timestamp from the request
        if mac not in records:
            return "DECLINE"
        else:
            current_time = datetime.now()
            message_time_with_space = records[mac]["Timestamp"][:10] + ' ' + records[mac]["Timestamp"][10:]
            record_time = datetime.fromisoformat(message_time_with_space)
            if current_time > record_time: # expired
                return "DECLINE"
            else: # not expired
                records[mac]['Acked'] = True 
                return f"ACKNOWLEDGE {records[mac]['MACAddress']} {records[mac]['IPAddress']} {records[mac]['Timestamp']}"
    elif request == "RELEASE":
        mac = parsed_message[1]  # Extract the MAC address from the request
        if mac in records:
            removed_record = records.pop(mac)  # Remove the client record
            current_time = datetime.now().isoformat()
            records[mac]['Timestamp'] = current_time # setting time to an expired time
            records[mac]['Acked'] = False 
        else:
            print("Server: Approved release request")
    elif request == "RENEW":
        mac = parsed_message[1]  # Extract the MAC address from the request
        ip = parsed_message[2]  # Extract the requested IP from the request
        timestamp = parsed_message[3]  # Extract the timestamp from the request

        if mac in records and records[mac]['IPAddress'] == ip:
            # If the client exists and the IP matches, update the timestamp and renew the lease
            records[mac]['Timestamp'] = timestamp
            return f"OFFER {records[mac]['MACAddress']} {records[mac]['IPAddress']} {records[mac]['Timestamp']}"
        else:
            return "DECLINE"  # Decline the renewal request if conditions are not met

    else:
        return f'INVALID REQUEST  {request}'  # Handle any unrecognized request type



# Start a UDP server
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Avoid TIME_WAIT socket lock [DO NOT REMOVE]
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("10.0.0.100", 9000))
print("DHCP Server running...")

try:
    while True:
        message, clientAddress = server.recvfrom(4096)
        parsed_message = parse_message(message.decode()) # parsed message is a list
        print("Server: Message received from server with request ") 
        print(parsed_message[0])
        response = dhcp_operation(parsed_message)
        server.sendto(response.encode(), clientAddress)
except OSError:
    pass
except KeyboardInterrupt:
    pass

server.close()