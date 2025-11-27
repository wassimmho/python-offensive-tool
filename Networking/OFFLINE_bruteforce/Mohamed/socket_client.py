import socket
import json
import time
import hashlib
import random
import os
import threading

# Define colors locally instead of importing from Server
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

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
HEADER = 64 
FORMAT = 'utf-8'
BUFFER_SIZE = 4096  # Add buffer size for recv()
SERVER_HOST = "192.168.100.66"  # Renamed for consistency
SERVER_PORT = 5050  # Renamed for consistency

# Worker State
client_socket = None
client_status = "CONNECTING"
client_id = f"worker-{random.randint(1000, 9999)}" # Unique ID for this worker instance

# --- Helper Functions ---

def send_message(conn, message_data):
    """Send a message with length-prefixed protocol"""
    try:
        # Convert dict to JSON string if needed
        if isinstance(message_data, dict):
            message_data = json.dumps(message_data)
        
        if isinstance(message_data, str):
            message_data = message_data.encode(FORMAT)
        
        # Create length header
        message_length = len(message_data)
        send_length = str(message_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        
        # Send header then data
        conn.sendall(send_length)
        conn.sendall(message_data)
        return True
    except Exception as e:
        print(f"{RED}Error sending message: {e}{RESET}")
        return False
    

def send_to_server(sock, data):
    """Sends JSON data reliably to the server."""
    try:
        # send_message handles dict to JSON conversion
        send_message(sock, data)
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
        computed_hash = hashlib.md5(pattern.encode('utf-8')).hexdigest()
        print(f"    [CHECK] Trying pattern: {pattern} => Hash: {computed_hash[:10]}...")
        
        if computed_hash == hash_value:
            print(f"    [SUCCESS] Pattern found: {pattern} for hash: {hash_value[:10]}...")
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

            # 1. Send initial system info for handshake (include client_id)
            send_message(client_socket, {"type": "STATUS", "status": client_status, "client_id": client_id})
            break
        

        except ConnectionRefusedError:
            print(f"[ERROR] Connection refused. Retrying in {reconnect_delay}s...")
        except socket.timeout:
            print(f"[ERROR] Connection timeout. Retrying in {reconnect_delay}s...")
        except socket.error as e:
            print(f"[ERROR] Socket error: {e}. Retrying in {reconnect_delay}s...")
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred: {e}. Retrying in {reconnect_delay}s...")
        
        # # Wait before attempting to reconnect
        # time.sleep(reconnect_delay)
        # reconnect_delay = min(reconnect_delay * 2, max_delay)
        # client_status = "DISCONNECTED"

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