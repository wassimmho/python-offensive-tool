import socket

HEADER = 64 
FORMAT = 'utf-8' 
DISCONNECT_MESSAGE = "!DISCONNECT" 

def setup_connection(server ,port , ClientName):
    ADDR = (server, port)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    client.send(ClientName)
    return client


def send(msg):
    message = msg.encode(FORMAT) 
    msg_length = len(message) 
    send_length = str(msg_length).encode(FORMAT) 
    send_length += b' ' * (HEADER - len(send_length)) 
    client.send(send_length) 
    client.send(message)

while True:
    print("Server Connection Settings:")
    server = input("Enter server IP (default: 192.168.100.250): ") or "192.168.100.250"
    port = input("Enter server port (default: 5050): ") or 5050
    name = input("Client name [auto]: ") or socket.gethostname()
    print(f"Connecting to server {server}:{port} as {name}...")
    client = setup_connection(server, port)
    msg = input("Enter message to send to server (or type '!DISCONNECT' to quit): ")
    send(msg)
    if msg == DISCONNECT_MESSAGE:
        break
send(DISCONNECT_MESSAGE)