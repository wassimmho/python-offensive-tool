import socket
import time
import GPUtil
import cpuinfo
import json
import base64
import os
import subprocess
import threading
import queue
from pathlib import Path
from Function_Net.recieving import receive_and_decompress_file
import hashlib
from OFFLINE_bruteforce.Mohamed import socket_client 


HEADER = 64 
FORMAT = 'utf-8'
server = "10.78.179.181"
port = 5555

# Global flags for stopping work
stop_work_flag = False
current_hash = None
stop_lock = threading.Lock()
message_queue = queue.Queue()  # Queue for passing messages from receiver thread to main thread

#===========colors============#

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def setup_connection(server, port, client_name, system_info):
    ADDR = (server, port)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    
    #========= Send client name
    name_bytes = client_name.encode(FORMAT)
    name_length = len(name_bytes)
    send_length = str(name_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    
    client.send(send_length)
    client.send(name_bytes)
    
    #=========Send system info
    system_info_json = json.dumps(system_info)
    system_info_bytes = system_info_json.encode(FORMAT)
    system_info_length = len(system_info_bytes)
    send_length = str(system_info_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    
    client.send(send_length)
    client.send(system_info_bytes)
    
    return client

def rate_cpu(cpu_info):
    """Rate CPU performance on a scale of 1-10"""
    cpu_name = cpu_info.get('brand_raw', '').lower()
    
    # High-end CPUs (8-10)
    if any(x in cpu_name for x in ['ryzen 9', 'threadripper', 'i9', 'xeon', 'epyc']):
        return 10
    elif any(x in cpu_name for x in ['ryzen 7', 'i7']):
        return 8
    
    # Mid-range CPUs (5-7)
    elif any(x in cpu_name for x in ['ryzen 5', 'i5']):
        return 6
    elif any(x in cpu_name for x in ['ryzen 3', 'i3']):
        return 5
    
    # Low-end CPUs (2-4)
    elif any(x in cpu_name for x in ['pentium', 'celeron', 'athlon']):
        return 3
    elif any(x in cpu_name for x in ['atom', 'sempron']):
        return 2
    
    # Default for unknown CPUs
    return 5

def rate_gpu(gpu):
    """Rate GPU performance on a scale of 1-10"""
    if not gpu or gpu.name == "No GPU detected":
        return 1
    
    gpu_name = gpu.name.lower()
    gpu_memory = gpu.memoryTotal
    
    # NVIDIA High-end (9-10)
    if any(x in gpu_name for x in ['rtx 4090', 'rtx 4080', 'a100', 'h100']):
        return 10
    elif any(x in gpu_name for x in ['rtx 4070', 'rtx 3090', 'rtx 3080']):
        return 9
    
    # NVIDIA Mid-high (7-8)
    elif any(x in gpu_name for x in ['rtx 3070', 'rtx 3060', 'rtx 4060']):
        return 8
    elif any(x in gpu_name for x in ['rtx 2080', 'rtx 2070', 'gtx 1080']):
        return 7
    
    # NVIDIA Mid-range (5-6)
    elif any(x in gpu_name for x in ['gtx 1660', 'gtx 1650', 'rtx 2060']):
        return 6
    elif any(x in gpu_name for x in ['gtx 1050', 'gtx 1060']):
        return 5
    
    # AMD High-end (8-10)
    elif any(x in gpu_name for x in ['rx 7900', 'rx 6900', 'radeon vii']):
        return 9
    elif any(x in gpu_name for x in ['rx 6800', 'rx 7800']):
        return 8
    
    # AMD Mid-range (5-7)
    elif any(x in gpu_name for x in ['rx 6700', 'rx 5700', 'rx 6600']):
        return 7
    elif any(x in gpu_name for x in ['rx 580', 'rx 590', 'rx 5600']):
        return 6
    elif any(x in gpu_name for x in ['rx 570', 'rx 560']):
        return 5
    
    # Low-end and integrated (2-4)
    elif any(x in gpu_name for x in ['mx', 'intel', 'uhd', 'iris']):
        return 3
    elif gpu_memory < 2000:  # Less than 2GB
        return 2
    elif gpu_memory < 4000:  # Less than 4GB
        return 4
    elif gpu_memory >= 8000:  # 8GB or more
        return 7
    
    # Default for unknown GPUs
    return 5

def receive_message(client_socket):

    try:

        client_socket.settimeout(10.0) 
        length_data = client_socket.recv(HEADER)
        if not length_data:
            return None
        
        message_length = int(length_data.decode(FORMAT).strip())
        

        timeout = max(10.0, (message_length / 1024) * 0.001 + 5.0)
        client_socket.settimeout(timeout)
        
        message_data = b""
        bytes_received = 0
        
        while bytes_received  < message_length:
            remaining = message_length - bytes_received
            chunk_size = min(65536, remaining) 

            chunk = client_socket.recv(chunk_size)
            
            if not chunk:
                return None
            
            message_data += chunk
            bytes_received += len(chunk)
            
            
            if message_length > 1048576: 
                progress = (bytes_received / message_length) * 100
                print(f"\r{BLUE}[*] Receiving file: {progress:.1f}%{RESET}", end="", flush=True)
        
        if message_length > 1048576:
            print() 
        return message_data
    
    except socket.timeout:
        return None
    except (ConnectionResetError, ConnectionAbortedError, OSError):
        raise
    except Exception as e:
        print(f"{RED}Error receiving the message: {e}{RESET}")
        return None

def get_system_info():
    ##------CPU Info------##
    cpu_info = cpuinfo.get_cpu_info()
    cpu_name = cpu_info.get('brand_raw', 'Unknown CPU')
    cpu_rating = rate_cpu(cpu_info)
    
    ##------GPU Info------##
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu_rating = rate_gpu(gpus[0])
        gpu_info = {
            "name": gpus[0].name,
            "memory_total": f"{gpus[0].memoryTotal}MB",
            "memory_used": f"{gpus[0].memoryUsed}MB",
            "rating": gpu_rating
        }
    else:
        gpu_info = {"name": "No GPU detected", "memory_total": "N/A", "memory_used": "N/A", "rating": 1}

    return {
        "cpu": cpu_name,
        "cpu_rating": cpu_rating,
        "gpu": gpu_info
    }



def brute_force_discovery(hash_value, start_range, end_range, length=6):
    """
    Simulates the actual brute-force work.
    This function will be called with the task payload.
    """
    # NOTE: The actual character set used must match the one used by the dispatcher.
    CHARACTERS = "abcdefghijklmnopqrstuvwxyz0123456789"
    
    # Helper function to convert index to pattern
    def index_to_pattern(index, length):
        pattern = ""
        temp_i = index
        for _ in range(length):
            pattern = CHARACTERS[temp_i % len(CHARACTERS)] + pattern
            temp_i //= len(CHARACTERS)
        return pattern
    
    start_pattern = index_to_pattern(start_range, length)
    end_pattern = index_to_pattern(end_range, length)
    
    print(f"{BLUE}    [TASK] Starting discovery for hash: {hash_value[:16]}...{RESET}")
    print(f"{BLUE}    [TASK] Range: {start_range:,} to {end_range:,} | Length: {length}{RESET}")
    print(f"{GREEN}    [TASK] Pattern range: {start_pattern} to {end_pattern}{RESET}")
    
    total_iterations = end_range - start_range + 1
    log_interval = max(1, total_iterations // 100)  # Log every 1%
    
    # Simple, non-recursive brute force for fixed length
    for i in range(start_range, end_range + 1):
        # Check if we should stop (another client found the pattern)
        with stop_lock:
            should_stop = stop_work_flag
        
        if should_stop:
            print(f"\n{YELLOW}    [STOPPED] Work stopped - pattern found by another worker{RESET}")
            return None
        
        pattern = ""
        temp_i = i
        
        # Convert index 'i' back into the character pattern
        for _ in range(length):
            pattern = CHARACTERS[temp_i % len(CHARACTERS)] + pattern
            temp_i //= len(CHARACTERS)
        
        # Use MD5 hash (matching the server's hash generation)
        computed_hash = hashlib.md5(pattern.encode('utf-8')).hexdigest()
        
        # Progress logging
        if (i - start_range) % log_interval == 0:
            progress = ((i - start_range) / total_iterations) * 100
            print(f"\r{YELLOW}    [PROGRESS] {progress:.1f}% - Trying: {pattern} => {computed_hash[:16]}...{RESET}", end="", flush=True)
        
        if computed_hash == hash_value:
            print(f"\n{GREEN}    [SUCCESS] Pattern found: {pattern} for hash: {hash_value}{RESET}")
            return pattern
    
    print(f"\n{RED}    [DONE] Pattern not found in range {start_range}-{end_range}{RESET}")
    return None # Pattern not found in this chunk

def message_receiver_thread(client):
    """Background thread to continuously receive ALL messages from server"""
    global stop_work_flag, current_hash
    
    while True:
        try:
            message_data = receive_message(client)
            
            if not message_data:
                continue
                
            message_str = message_data.decode(FORMAT)
            
            try:
                broadcast_msg = json.loads(message_str)
                msg_type = broadcast_msg.get("type")
                
                if msg_type == "STOP_WORK":
                    hash_value = broadcast_msg.get("hash")
                    found_by = broadcast_msg.get("found_by")
                    pattern = broadcast_msg.get("pattern", "unknown")
                    
                    # Set global stop flag with thread safety
                    with stop_lock:
                        if current_hash == hash_value:
                            stop_work_flag = True
                    
                    print(f"\n{GREEN}┌{'─'*78}┐{RESET}")
                    print(f"{GREEN}│{RESET} {BLUE}🎉 PATTERN FOUND BY ANOTHER WORKER{RESET}                                      {GREEN}│{RESET}")
                    print(f"{GREEN}├{'─'*78}┤{RESET}")
                    print(f"{GREEN}│{RESET}   Found by: {YELLOW}{found_by:<60}{RESET} {GREEN}│{RESET}")
                    print(f"{GREEN}│{RESET}   Pattern: {YELLOW}{pattern:<61}{RESET} {GREEN}│{RESET}")
                    print(f"{GREEN}│{RESET}   Stopping local work...{' '*49}{RESET} {GREEN}│{RESET}")
                    print(f"{GREEN}└{'─'*78}┘{RESET}")
                
                elif msg_type in ["BROADCASTING", "CMD_EXEC"]:
                    # Put work messages in queue for main thread to process
                    message_queue.put((msg_type, broadcast_msg))
                    
            except json.JSONDecodeError:
                pass
                
        except socket.timeout:
            continue
        except (ConnectionResetError, ConnectionAbortedError, OSError):
            message_queue.put(("CONNECTION_CLOSED", None))
            break
        except Exception as e:
            print(f"{RED}[ERROR] Message receiver thread: {e}{RESET}")
            break


if __name__ == "__main__":
    print("═" * 80)
    print("              CLIENT - Connecting to Server")
    print("═" * 80)
    
   

    name =  socket.gethostname()
    
    print(f"\n[*] Connecting to server {server}:{port} as '{name}'...")
    print(f"[*] Gathering system information...")
    
    try:
        system_info = get_system_info()
        client = setup_connection(server, port, name, system_info)
        print(f"Successfully connected to {server}:{port}")
        print(f"Client name '{name}' sent to server")
        print(f"System information sent to server")
        print("\nConnection established. Client is now registered with the server.")
        print("Press Ctrl+C to disconnect...\n")
        
        # Start background thread to receive ALL messages
        receiver_thread = threading.Thread(target=message_receiver_thread, args=(client,), daemon=True)
        receiver_thread.start()
        
        while True:
            try:
                # Get message from queue (with timeout to allow KeyboardInterrupt)
                try:
                    msg_type, msg_data = message_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                
                if msg_type == "CONNECTION_CLOSED":
                    print(f"\n{YELLOW}┌{'─'*78}┐{RESET}")
                    print(f"{YELLOW}│{RESET} {BLUE}ℹ DISCONNECTED BY SERVER{RESET}                                               {YELLOW}│{RESET}")
                    print(f"{YELLOW}├{'─'*78}┤{RESET}")
                    print(f"{YELLOW}│{RESET}   The server has closed the connection.                                  {YELLOW}│{RESET}")
                    print(f"{YELLOW}│{RESET}   This may be due to a server-side disconnect command.                   {YELLOW}│{RESET}")
                    print(f"{YELLOW}└{'─'*78}┘{RESET}")
                    print("\nPress Enter to exit...")
                    input()
                    break
                
                if msg_type == "BROADCASTING":
                    stop_work_flag, current_hash
                    
                    broadcast_msg = msg_data
                    hash_value = broadcast_msg.get("hash_value")
                    entry_id = broadcast_msg.get("entry_id", "unknown")
                    start_range = broadcast_msg.get("start_range", 0)
                    end_range = broadcast_msg.get("end_range", 90000000)
                    pattern_length = broadcast_msg.get("pattern_length", 6)
                    
                    # Get the worker_id from socket_client module
                    worker_id = socket_client.client_id
                    
                    # Reset stop flag and set current hash with thread safety
                    with stop_lock:
                        stop_work_flag = False
                        current_hash = hash_value
                    
                    print(f"{BLUE}[*] Starting worker with ID: {worker_id}{RESET}")
                    print(f"{YELLOW}[*] Received hash to crack: {hash_value} (Entry: {entry_id}){RESET}")
                    print(f"{BLUE}[*] Assigned range: {start_range:,} to {end_range:,} (Length: {pattern_length}){RESET}")
                    print(f"{BLUE}[*] Total combinations to check: {end_range - start_range + 1:,}{RESET}")
                    
                    # Send worker_id to server
                    worker_info = json.dumps({"type": "WORKER_ID", "worker_id": worker_id})
                    worker_info_bytes = worker_info.encode(FORMAT)
                    worker_info_length = len(worker_info_bytes)
                    send_length = str(worker_info_length).encode(FORMAT)
                    send_length += b' ' * (HEADER - len(send_length))
                    client.send(send_length)
                    client.send(worker_info_bytes)
                    
                    # Send status update to server (WORKING)
                    status_msg = json.dumps({"type": "STATUS", "status": "WORKING", "worker_id": worker_id})
                    status_bytes = status_msg.encode(FORMAT)
                    status_length = len(status_bytes)
                    send_length = str(status_length).encode(FORMAT)
                    send_length += b' ' * (HEADER - len(send_length))
                    client.send(send_length)
                    client.send(status_bytes)
                    
                    # Run brute force discovery with the assigned range
                    print(f"{BLUE}[*] Worker {worker_id} is now working on assigned checkpoint...{RESET}")
                    result = brute_force_discovery(hash_value, start_range, end_range, length=pattern_length)
                    
                    # Send result back to server
                    if result:
                        print(f"{GREEN}[*] Worker {worker_id} found the pattern: {result}{RESET}")
                        result_msg = json.dumps({"type": "RESULT", "status": "CRACKED", "pattern": result, "worker_id": worker_id, "hash": hash_value})
                    else:
                        print(f"{YELLOW}[*] Worker {worker_id} completed range {start_range:,}-{end_range:,} - pattern not found{RESET}")
                        result_msg = json.dumps({"type": "RESULT", "status": "NOT_FOUND", "worker_id": worker_id, "hash": hash_value})
                    
                    result_bytes = result_msg.encode(FORMAT)
                    result_length = len(result_bytes)
                    send_length = str(result_length).encode(FORMAT)
                    send_length += b' ' * (HEADER - len(send_length))
                    client.send(send_length)
                    client.send(result_bytes)
                    
                    # Send status update to server (IDLE)
                    status_msg = json.dumps({"type": "STATUS", "status": "IDLE", "worker_id": worker_id})
                    status_bytes = status_msg.encode(FORMAT)
                    status_length = len(status_bytes)
                    send_length = str(status_length).encode(FORMAT)
                    send_length += b' ' * (HEADER - len(send_length))
                    client.send(send_length)
                    client.send(status_bytes)
                    
                    print(f"{GREEN}[*] Worker {worker_id} has completed its assigned checkpoint.{RESET}")
                
                elif msg_type == "CMD_EXEC":
                    broadcast_msg = msg_data
                    command = broadcast_msg.get("command")
                    print(f"{BLUE}[*] Received command: {command}{RESET}")
                    
                    try:
                        if command.lower().startswith("cd "):
                            try:
                                target_dir = command[3:].strip()
                                os.chdir(target_dir)
                                output = f"Changed directory to {os.getcwd()}"
                            except Exception as e:
                                output = str(e)
                        else:
                            process = subprocess.Popen(
                                command, 
                                shell=True, 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE
                            )
                            stdout, stderr = process.communicate()
                            output = stdout.decode('utf-8', errors='replace') + stderr.decode('utf-8', errors='replace')
                        
                        if not output:
                            output = "[Command executed successfully with no output]"
                            
                    except Exception as e:
                        output = f"Error executing command: {str(e)}"
                    
                    # Send output back
                    response = json.dumps({
                        "type": "CMD_OUTPUT", 
                        "output": output,
                        "cwd": os.getcwd()
                    })
                    
                    response_bytes = response.encode(FORMAT)
                    response_length = len(response_bytes)
                    send_length = str(response_length).encode(FORMAT)
                    send_length += b' ' * (HEADER - len(send_length))
                    client.send(send_length)
                    client.send(response_bytes)
            
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(f"{RED}[ERROR] Main loop exception: {e}{RESET}")
                continue
            
    except ConnectionRefusedError:
        print(f"Failed to connect to {server}:{port}")
        print("Make sure the server is running and the address is correct.")
        print("\nPress Enter to exit...")
        input()
    except KeyboardInterrupt:
        print("\nDisconnecting from server...")
        client.close()
        print("Connection closed.")
        print("\nPress Enter to exit...")
        input()
    except Exception as e:
        print(f"An error occurred: {e}")
        if 'client' in locals():
            client.close()
        print("\nPress Enter to exit...")
        input()
    finally:
        if 'client' in locals():
            try:
                client.close()
            except:
                pass
