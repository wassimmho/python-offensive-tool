import socket
import time
import GPUtil
import cpuinfo
import json
import base64
import os
from pathlib import Path


HEADER = 64 
FORMAT = 'utf-8'

# ANSI escape codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

def setup_connection(server, port, client_name, system_info):
    ADDR = (server, port)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    
    # Send client name
    name_bytes = client_name.encode(FORMAT)
    name_length = len(name_bytes)
    send_length = str(name_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    
    client.send(send_length)
    client.send(name_bytes)
    
    # Send system info
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

def base64_archive_to_files(encoded_string, output_dir="received_files"):
    """Decode base64 string and extract zip archive"""
    try:
        import zipfile
        import io
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Decode base64
        raw = base64.b64decode(encoded_string)
        buf = io.BytesIO(raw)
        
        # Extract zip archive
        with zipfile.ZipFile(buf, "r") as z:
            z.extractall(output_dir)
        
        return True, output_dir
    except Exception as e:
        return False, str(e)

def receive_message(client_socket):
    """Receive a complete message using length-prefixed protocol"""
    try:
        # Receive message length header
        length_data = client_socket.recv(HEADER)
        if not length_data:
            return None
        
        message_length = int(length_data.decode(FORMAT).strip())
        
        # Receive the actual message data
        message_data = b""
        bytes_received = 0
        
        while bytes_received < message_length:
            chunk = client_socket.recv(min(4096, message_length - bytes_received))
            if not chunk:
                print(f"{RED}Connection closed while receiving message{RESET}")
                return None
            message_data += chunk
            bytes_received += len(chunk)
        
        return message_data
    except Exception as e:
        print(f"{RED}Error receiving message: {e}{RESET}")
        return None

def handle_file_message(message_data):
    """Handle incoming file archive from server"""
    try:
        msg = json.loads(message_data.decode(FORMAT))
        
        if msg.get("type") == "file_archive":
            filename = msg.get("filename", "files.zip")
            encoded_data = msg.get("data", "")
            
            success, result = base64_archive_to_files(encoded_data)
            
            if success:
                print(f"\n{GREEN}┌{'─'*78}┐{RESET}")
                print(f"{GREEN}│{RESET} {BLUE}✓ FILES RECEIVED{RESET}                                                          {GREEN}│{RESET}")
                print(f"{GREEN}├{'─'*78}┤{RESET}")
                print(f"{GREEN}│{RESET}   Archive: {YELLOW}{filename:<60}{RESET} {GREEN}│{RESET}")
                print(f"{GREEN}│{RESET}   Location: {YELLOW}{os.path.abspath(result):<56}{RESET} {GREEN}│{RESET}")
                print(f"{GREEN}└{'─'*78}┘{RESET}")
                return True
            else:
                print(f"{RED}Error extracting files: {result}{RESET}")
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


if __name__ == "__main__":
    print("═" * 80)
    print("              CLIENT - Connecting to Server")
    print("═" * 80)
    
    #server = input("\nEnter server IP (default: 192.168.100.250): ") or "192.168.100.250"
    server = "192.168.43.181"
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
                client.settimeout(2.0)
                message_data = receive_message(client)
                
                if message_data:
                    handle_file_message(message_data)
                else:
                    # Connection closed by server
                    print(f"\n{YELLOW}[*] Server closed the connection{RESET}")
                    break
                    
            except socket.timeout:
                continue
            except OSError as e:
                print(f"\n{RED}┌{'─'*78}┐{RESET}")
                print(f"{RED}│{RESET} {YELLOW} CONNECTION LOST{RESET}                                                      {RED}│{RESET}")
                print(f"{RED}├{'─'*78}┤{RESET}")
                print(f"{RED}│{RESET}   Connection to server was forcibly closed.                              {RED}│{RESET}")
                print(f"{RED}│{RESET}   Error: {str(e):<63}{RED}│{RESET}")
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