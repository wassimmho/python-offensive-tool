import socket
import time
import GPUtil
import cpuinfo
import json
import base64
import os
import sys
from pathlib import Path
from Function_Net.recieving import receive_and_decompress_file
import hashlib
from OFFLINE_bruteforce.Mohamed import socket_client 

# Fix encoding for hidden console windows
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

HEADER = 64 
FORMAT = 'utf-8'
server = "192.168.100.66"
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
                print(f"{RED}Connection closed while receiving message{RESET}")
                return None
            
            message_data += chunk
            bytes_received += len(chunk)
            
            
            if message_length > 1048576: 
                progress = (bytes_received / message_length) * 100
                print(f"\r{BLUE}[*] Receiving file: {progress:.1f}%{RESET}", end="", flush=True)
        
        print() 
        return message_data
    
    except socket.timeout:
        return None
    except ConnectionResetError:
        # Server forcibly closed the connection (WinError 10054)
        raise  # Re-raise to be handled by the main loop
    except ConnectionAbortedError:
        # Connection was aborted
        raise  # Re-raise to be handled by the main loop
    except OSError as e:
        # Check for connection reset errors (WinError 10054, 10053)
        if e.winerror in (10054, 10053):
            raise  # Re-raise to be handled by the main loop
        print(f"{RED}Error receiving the message: {e}{RESET}")
        return None
    except Exception as e:
        print(f"{RED}Error receiving the message: {e}{RESET}")
        return None

def handle_file_message(message_data):
    try:
        msg = json.loads(message_data.decode(FORMAT))
        
        if msg.get("type") == "file_archive":
            filename = msg.get("filename", "received_file")
            encoded_data = msg.get("data", "")
            
            result = receive_and_decompress_file(encoded_data, filename, output_dir="logs/files")
            
            if result['success']:
                print(f"\n{GREEN}┌{'─'*78}┐{RESET}")
                print(f"{GREEN}│{RESET} {BLUE}✓ FILE RECEIVED{RESET}                                                          {GREEN}│{RESET}")
                print(f"{GREEN}├{'─'*78}┤{RESET}")
                print(f"{GREEN}│{RESET}   File:   {YELLOW}{filename:<60}{RESET} {GREEN}│{RESET}")
                print(f"{GREEN}│{RESET}   Size:   {YELLOW}{result['original_size']} bytes{' '*(48-len(str(result['original_size'])))}{RESET} {GREEN}│{RESET}")
                print(f"{GREEN}│{RESET}   Location: {YELLOW}{result['path']:<54}{RESET} {GREEN}│{RESET}")
                print(f"{GREEN}└{'─'*78}┘{RESET}")
                return True
            else:
                print(f"{RED}Error receiving file: {result['message']}{RESET}")
                return False
    except json.JSONDecodeError:
        print(f"{RED}Error decoding file message{RESET}")
        return False
    except Exception as e:
        print(f"{RED}Error handling file: {e}{RESET}")
        return False

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
    
    print(f"{BLUE}    [TASK] Starting discovery for hash: {hash_value[:16]}...{RESET}")
    print(f"{BLUE}    [TASK] Range: {start_range} to {end_range} | Length: {length}{RESET}")
    
    total_iterations = end_range - start_range + 1
    log_interval = max(1, total_iterations // 100)  # Log every 1%
    
    # Simple, non-recursive brute force for fixed length
    for i in range(start_range, end_range + 1):
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

if __name__ == "__main__":
    print("═" * 80)
    print("              CLIENT - Connecting to Server")
    print("═" * 80)
    
    #server = input("\nEnter server IP (default: 192.168.100.250): ") or "192.168.100.250"
    #port_input = input("Enter server port (default: 5050): ") or "5050"
    port = 5050
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
        
        
        while True:
            try:
                message_data = receive_message(client)
                
                # if message_data:
                #     handle_file_message(message_data)
                if message_data:
                    message_str = message_data.decode(FORMAT)
                    
                    # Try to parse as JSON first (new format with hash)
                    try:
                        broadcast_msg = json.loads(message_str)
                        if broadcast_msg.get("type") == "BROADCASTING":
                            hash_value = broadcast_msg.get("hash_value")
                            entry_id = broadcast_msg.get("entry_id", "unknown")
                            
                            # Get the worker_id from socket_client module
                            worker_id = socket_client.client_id
                            print(f"{BLUE}[*] Starting worker with ID: {worker_id}{RESET}")
                            print(f"{YELLOW}[*] Received hash to crack: {hash_value} (Entry: {entry_id}){RESET}")
                            
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
                            
                            # Run brute force discovery with the received hash
                            print(f"{BLUE}[*] Worker with ID: {worker_id} is now working...{RESET}")
                            result = brute_force_discovery(hash_value, 0, 90000000, length=6)
                            
                            # Send result back to server
                            if result:
                                print(f"{GREEN}[*] Worker with ID: {worker_id} found the pattern: {result}{RESET}")
                                result_msg = json.dumps({"type": "RESULT", "status": "CRACKED", "pattern": result, "worker_id": worker_id, "hash": hash_value})
                            else:
                                print(f"{YELLOW}[*] Worker with ID: {worker_id} did not find pattern in range.{RESET}")
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
                            
                            print(f"{GREEN}[*] Worker with ID: {worker_id} has completed its task.{RESET}")
                            continue
                    except json.JSONDecodeError:
                        pass
                    
                    # Fallback for old format (plain "BROADCASTING" string)
                    if message_str == "BROADCASTING":
                        # Get the worker_id from socket_client module
                        worker_id = socket_client.client_id
                        print(f"{BLUE}[*] Starting worker with ID: {worker_id}{RESET}")
                        
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
                        
                        # Run brute force with default hash
                        print(f"{BLUE}[*] Worker with ID: {worker_id} is now working...{RESET}")
                        result = brute_force_discovery('4773a5f2a66b3d29393803ba631c3491', 0, 100000, length=6)
                        
                        if result:
                            print(f"{GREEN}[*] Worker with ID: {worker_id} found the pattern: {result}{RESET}")
                        else:
                            print(f"{YELLOW}[*] Worker with ID: {worker_id} did not find pattern in range.{RESET}")
                        
                        # Send status update to server (IDLE)
                        status_msg = json.dumps({"type": "STATUS", "status": "IDLE", "worker_id": worker_id})
                        status_bytes = status_msg.encode(FORMAT)
                        status_length = len(status_bytes)
                        send_length = str(status_length).encode(FORMAT)
                        send_length += b' ' * (HEADER - len(send_length))
                        client.send(send_length)
                        client.send(status_bytes)
                        
                        print(f"{GREEN}[*] Worker with ID: {worker_id} has completed its task.{RESET}")
                    
            except socket.timeout:
                continue
            except (ConnectionResetError, ConnectionAbortedError):
                # Server disconnected us gracefully or forcibly
                print(f"\n{YELLOW}┌{'─'*78}┐{RESET}")
                print(f"{YELLOW}│{RESET} {BLUE}ℹ DISCONNECTED BY SERVER{RESET}                                               {YELLOW}│{RESET}")
                print(f"{YELLOW}├{'─'*78}┤{RESET}")
                print(f"{YELLOW}│{RESET}   The server has closed the connection.                                  {YELLOW}│{RESET}")
                print(f"{YELLOW}│{RESET}   This may be due to a server-side disconnect command.                   {YELLOW}│{RESET}")
                print(f"{YELLOW}└{'─'*78}┘{RESET}")
                print("\nPress Enter to exit...")
                input()
                break
            except OSError as e:
                # Check for specific Windows socket errors
                if hasattr(e, 'winerror') and e.winerror in (10054, 10053):
                    # 10054 = Connection reset by peer
                    # 10053 = Connection aborted
                    print(f"\n{YELLOW}┌{'─'*78}┐{RESET}")
                    print(f"{YELLOW}│{RESET} {BLUE}ℹ DISCONNECTED BY SERVER{RESET}                                               {YELLOW}│{RESET}")
                    print(f"{YELLOW}├{'─'*78}┤{RESET}")
                    print(f"{YELLOW}│{RESET}   The server has closed the connection.                                  {YELLOW}│{RESET}")
                    print(f"{YELLOW}│{RESET}   This may be due to a server-side disconnect command.                   {YELLOW}│{RESET}")
                    print(f"{YELLOW}└{'─'*78}┘{RESET}")
                else:
                    print(f"\n{RED}┌{'─'*78}┐{RESET}")
                    print(f"{RED}│{RESET} {YELLOW}⚠ CONNECTION ERROR{RESET}                                                     {RED}│{RESET}")
                    print(f"{RED}├{'─'*78}┤{RESET}")
                    print(f"{RED}│{RESET}   An unexpected network error occurred.                                  {RED}│{RESET}")
                    error_str = str(e)[:60]
                    padding = 63 - len(error_str)
                    print(f"{RED}│{RESET}   Error: {error_str}{' '*padding}{RED}│{RESET}")
                    print(f"{RED}└{'─'*78}┘{RESET}")
                print("\nPress Enter to exit...")
                input()
                break
            
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