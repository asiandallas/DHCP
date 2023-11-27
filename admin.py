# We assume there is also another type of client named admin. 
# When we run the admin client, it will send a LIST message to the server.
# When the server receives the LIST message, it will send the contents of its records to the admin client. 
# The admin client will receive that and display its content as a list of records.

import socket

SERVER_IP = "10.0.0.100"
SERVER_PORT = 9000


# Start a UDP server
admin = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Avoid TIME_WAIT socket lock [DO NOT REMOVE]
admin.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
admin.bind(("10.0.0.100", 9000))

try:
    while True:
        message, clientAddress = server.recvfrom(4096)
        parsed_message = parse_message(message.decode()) # parsed message is a list
        print("Server: Message received from server with request ") 
        print(parsed_message[0])
        admin.sendto(response.encode(), clientAddress)
except OSError:
    pass
except KeyboardInterrupt:
    pass

admin.close()

    