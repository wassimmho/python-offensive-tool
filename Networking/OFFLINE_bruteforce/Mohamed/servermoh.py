# main_server.py (The Socket Server, Task Broker, and Task Dispatcher UI Combined)

import socket
import threading
import json
import time
import sys
from config import SERVER_HOST, SERVER_PORT, CELERY_BROKER_URL
from task_broker import TaskBroker, client_status_lock, CLIENT_CONNECTIONS # Import globals and TaskBroker
from task_dispatcher import main as dispatcher_main # Import dispatcher logic

# --- Global State Management ---
# CLIENT_CONNECTIONS is imported from task_broker.py 
CRACKED_PATTERNS = {} # {task_id: pattern}

# External references (can be set by parent server)
_external_clients = None
_external_clients_lock = None

# --- Core Socket Communication Handlers ---

def handle_client_message(conn, addr, broker_ref):
    """Handles incoming data from a single connected client."""
    buffer = ""
    client_name = f"Client-{addr[1]}" # Default name until client sends STATUS_UPDATE

    try:
        # Initial registration and welcome message
        with client_status_lock:
            client_name = CLIENT_CONNECTIONS[addr].get("name", f"Client-{addr[1]}")
            
        welcome_msg = json.dumps({"type": "SERVER_INFO", "message": f"Connected. Your ID: {client_name}"}) + '\n'
        conn.sendall(welcome_msg.encode('utf-8'))
        
        while True:
            # Receive data chunk by chunk
            data = conn.recv(4096).decode('utf-8')
            if not data:
                break # Connection closed by client
            
            buffer += data
            
            # Use newline as the message delimiter
            messages = buffer.split('\n')
            buffer = messages.pop() # Keep incomplete message fragment

            for msg_str in messages:
                if not msg_str.strip():
                    continue

                try:
                    message = json.loads(msg_str)
                    
                    if message.get("type") == "STATUS_UPDATE":
                        # Client sending its current status (e.g., IDLE)
                        client_name = message.get("name", client_name)
                        status = message.get("status", "IDLE")
                        with client_status_lock:
                            if addr in CLIENT_CONNECTIONS:
                                CLIENT_CONNECTIONS[addr]["name"] = client_name
                                CLIENT_CONNECTIONS[addr]["status"] = status
                        print(f"[{time.strftime('%H:%M:%S')}] [STATUS] {client_name} is now {status}.")
                        
                    elif message.get("type") == "TASK_RESULT":
                        # Client finished a task and returned the result
                        task_id = message['task_id']
                        result = message['result']
                        worker_name = message.get('worker', client_name)

                        if result['found']:
                            pattern = result['pattern']
                            CRACKED_PATTERNS[task_id] = pattern
                            print(f"\n=======================================================")
                            print(f"🎉 CRACK FOUND by {worker_name} for Task {task_id[:8]}...: **{pattern}**")
                            print(f"Time taken: {result['duration']}")
                            print(f"=======================================================\n")
                        else:
                            print(f"[{time.strftime('%H:%M:%S')}] [RESULT] Task {task_id[:8]}... completed by {worker_name} (Not Found, {result['duration']}).")

                        # Task is done, the TaskBroker will pick up the IDLE status next
                    
                except json.JSONDecodeError:
                    print(f"[{time.strftime('%H:%M:%S')}] [CLIENT ERROR] Invalid JSON from {client_name}: {msg_str}")
                
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] [ERROR] Connection error with {client_name} ({addr}): {e}")
    finally:
        # Client disconnected, remove from active list
        print(f"[{time.strftime('%H:%M:%S')}] [DISCONNECT] {client_name} disconnected.")
        try:
            conn.close()
        except:
            pass
            
        with client_status_lock:
            if addr in CLIENT_CONNECTIONS:
                del CLIENT_CONNECTIONS[addr]

def socket_listener(broker_ref):
    """Sets up the server socket and listens for client connections."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((SERVER_HOST, SERVER_PORT))
        server.listen(10)
        print(f"[{time.strftime('%H:%M:%S')}] Socket Server listening on {SERVER_HOST}:{SERVER_PORT}")
        
        while True:
            conn, addr = server.accept()
            print(f"[{time.strftime('%H:%M:%S')}] New connection established with {addr}")
            
            with client_status_lock:
                CLIENT_CONNECTIONS[addr] = {"conn": conn, "name": f"Client-{addr[1]}", "status": "IDLE"}
                
            # Start a new thread to handle incoming messages from this client
            client_handler = threading.Thread(target=handle_client_message, args=(conn, addr, broker_ref))
            client_handler.daemon = True
            client_handler.start()

    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] [FATAL] Server setup error: {e}")
    finally:
        try:
            server.close()
        except:
            pass


def main(external_clients=None, external_lock=None, skip_socket_listener=False):
    """Starts the three main components: Listener, Broker, and Dispatcher UI.
    
    Args:
        external_clients: Optional dict of clients from parent server
        external_lock: Optional threading.Lock from parent server
        skip_socket_listener: If True, don't start socket listener (use parent's clients)
    """
    global _external_clients, _external_clients_lock
    
    _external_clients = external_clients
    _external_clients_lock = external_lock
    
    # Use external clients if provided, otherwise use internal CLIENT_CONNECTIONS
    clients_to_use = external_clients if external_clients is not None else CLIENT_CONNECTIONS
    
    print("=====================================================")
    print("STARTING DISTRIBUTED HASH DISCOVERY SERVER")
    print(f"Redis Broker: {CELERY_BROKER_URL}")
    if not skip_socket_listener:
        print(f"Socket Server: {SERVER_HOST}:{SERVER_PORT}")
    else:
        print(f"Using external client pool ({len(clients_to_use)} clients)")
    print("=====================================================")

    # 1. Start the TaskBroker thread (The Celery <-> Socket Bridge)
    broker = TaskBroker(clients_to_use, external_lock)
    broker.daemon = True
    broker.start()
    
    # 2. Start the Socket Listener thread (only if not using external clients)
    if not skip_socket_listener:
        listener_thread = threading.Thread(target=socket_listener, args=(broker,))
        listener_thread.daemon = True
        listener_thread.start()

    # 3. Start the Dispatcher UI (Main thread, blocking for user input)
    try:
        dispatcher_main(broker) # Pass the broker reference to the dispatcher UI
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received.")
    finally:
        broker.stop()
        print("System shutdown complete.")

if __name__ == "__main__":
    main()