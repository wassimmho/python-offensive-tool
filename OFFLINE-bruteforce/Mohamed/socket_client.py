import socket
import json
import time
import hashlib
import random
import os
import threading

# --- Firebase Setup (Required for Canvas Environment) ---
# Although this client doesn't use Firestore, these globals must be defined.
try:
    __app_id = os.environ.get('__app_id', 'default-app-id')
    __firebase_config = os.environ.get('__firebase_config', '{}')
    __initial_auth_token = os.environ.get('__initial_auth_token', None)
except:
    # Fallback in case environment variables are not available
    __app_id = 'default-app-id'
    __firebase_config = '{}'
    __initial_auth_token = None
# --------------------------------------------------------


# --- Configuration ---
# NOTE: Replace these with your actual server host and port
SERVER_HOST = "127.0.0.1" 
SERVER_PORT = 9999
BUFFER_SIZE = 1024

# Worker State
client_socket = None
client_status = "CONNECTING"
client_id = f"worker-{random.randint(1000, 9999)}" # Unique ID for this worker instance

# --- Helper Functions ---

def generate_system_info():
    """Generates mock system info for initial handshake."""
    return {
        "client_id": client_id,
        "client_name": f"Distributed Worker {client_id.split('-')[-1]}",
        "cpu": "Intel Core i7 (Mock)",
        "cpu_rating": 8000,
        "gpu": {"name": "NVIDIA RTX 3080 (Mock)", "rating": 12000},
        "system_type": "distributed_worker"
    }

def send_to_server(sock, data):
    """Sends JSON data reliably to the server."""
    try:
        message = json.dumps(data)
        sock.sendall(message.encode('utf-8') + b'\n') # Use newline delimiter
    except Exception as e:
        print(f"[ERROR] Failed to send data: {e}")
        return False
    return True

def brute_force_discovery(hash_value, start_range, end_range, length=6):
    """
    Simulates the actual brute-force work.
    This function will be called with the task payload.
    """
    # NOTE: The actual character set used must match the one used by the dispatcher.
    CHARACTERS = "abcdefghijklmnopqrstuvwxyz01234456789"
    
    print(f"    [TASK] Starting discovery for hash: {hash_value[:10]}... from {start_range} to {end_range}")
    
    # Simple, non-recursive brute force for fixed length
    for i in range(start_range, end_range + 1):
        pattern = ""
        temp_i = i
        
        # Convert index 'i' back into the character pattern
        for _ in range(length):
            pattern = CHARACTERS[temp_i % len(CHARACTERS)] + pattern
            temp_i //= len(CHARACTERS)
            
        # Simulate the check
        computed_hash = hashlib.sha256(pattern.encode('utf-8')).hexdigest()
        
        if computed_hash == hash_value:
            return pattern
            
    return None # Pattern not found in this chunk

# --- Main Socket Handler ---

def run_client():
    global client_socket, client_status
    
    # Exponential backoff for reconnection
    reconnect_delay = 1
    max_delay = 60

    while True:
        try:
            if client_socket:
                client_socket.close()
                client_socket = None
            
            print(f"[CONN] Attempting to connect to {SERVER_HOST}:{SERVER_PORT}...")
            client_status = "CONNECTING"
            
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            client_status = "IDLE"
            reconnect_delay = 1 # Reset delay on successful connection
            print(f"\n[CONN] Successfully connected! ID: {client_id}")

            # 1. Send initial system info for handshake
            send_to_server(client_socket, generate_system_info())
            send_to_server(client_socket, {"type": "STATUS", "status": client_status})

            # 2. Main listening loop
            while True:
                # The server sends tasks and commands as JSON messages
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    print("[CONN] Server closed the connection.")
                    break
                
                # Assuming the server sends a single task command per packet
                try:
                    message_str = data.decode('utf-8').strip()
                    task = json.loads(message_str)
                    
                    if task.get("type") == "TASK":
                        threading.Thread(target=process_task, args=(task,)).start()
                        
                except json.JSONDecodeError:
                    # Handle cases where multiple JSON objects are in one buffer or incomplete
                    # For simplicity, we just log the raw data.
                    print(f"[RECV] Received raw data (possible split): {data.decode('utf-8').strip()}")
                except Exception as e:
                    print(f"[ERROR] Error processing received data: {e}")

        except ConnectionRefusedError:
            print(f"[ERROR] Connection refused. Retrying in {reconnect_delay}s...")
        except socket.timeout:
            print(f"[ERROR] Connection timeout. Retrying in {reconnect_delay}s...")
        except socket.error as e:
            print(f"[ERROR] Socket error: {e}. Retrying in {reconnect_delay}s...")
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred: {e}. Retrying in {reconnect_delay}s...")
        
        # Wait before attempting to reconnect
        time.sleep(reconnect_delay)
        reconnect_delay = min(reconnect_delay * 2, max_delay)
        client_status = "DISCONNECTED"

def process_task(task_data):
    """Handles task processing in a separate thread."""
    global client_status
    
    # Extract task details
    job_id = task_data.get("job_id")
    entry_id = task_data.get("entry_id")
    hash_value = task_data.get("hash")
    start_range = task_data.get("start_range")
    end_range = task_data.get("end_range")

    if not all([job_id, entry_id, hash_value, start_range is not None, end_range is not None]):
        print(f"[TASK] Invalid task received: {task_data}")
        return

    print(f"\n[TASK] Received Task {job_id[:8]}... for Entry {entry_id[:8]}...")
    
    # 1. Set status to WORKING
    client_status = "WORKING"
    send_to_server(client_socket, {"type": "STATUS", "status": client_status, "job_id": job_id})

    # 2. Execute the work (blocking operation)
    cracked_pattern = brute_force_discovery(hash_value, start_range, end_range)

    # 3. Prepare result message
    result_message = {
        "type": "RESULT",
        "job_id": job_id,
        "entry_id": entry_id,
        "client_id": client_id,
        "time_completed": time.time()
    }

    if cracked_pattern:
        result_message["status"] = "CRACKED"
        result_message["pattern"] = cracked_pattern
        print(f"[RESULT] Pattern cracked: {cracked_pattern}")
    else:
        result_message["status"] = "NOT_FOUND"
        print(f"[RESULT] Pattern not found in chunk.")

    # 4. Send result back to server
    send_to_server(client_socket, result_message)

    # 5. Set status back to IDLE
    client_status = "IDLE"
    send_to_server(client_socket, {"type": "STATUS", "status": client_status})
    print(f"[STATUS] Client is now IDLE, awaiting next task.")
    
    # Re-prompt server command line
    print(f"Server> ", end="", flush=True)


if __name__ == "__main__":
    run_client()