import socket
import threading
import os
import json
import time
import sys
import sqlite3
import hashlib
import itertools
import math
from Function_Net.sending import files_to_base64, base64_to_file, files_to_base64_archive, base64_archive_to_files, selecting_files
from Function_Net.recieving import receive_and_decompress_file, receive_multiple_files, receive_file_simple
from tkinter import Tk, filedialog
from OFFLINE_bruteforce.Mohamed.socket_client import brute_force_discovery

##--------------------------ANSI escape codes-----------------------------##
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
##------------------------------------------------------------------------##

# Try to import Celery components (optional - for distributed hash discovery)
try:
    from celery import chord, group
    from OFFLINE_bruteforce.Mohamed.socket_tasks import package_socket_task, handle_completion_callback
    from OFFLINE_bruteforce.Mohamed.config import MAX_PATTERN_LENGTH, CHARACTER_SET, CELERY_BROKER_URL
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    print(f"{YELLOW}[WARNING] Celery not available. Hash discovery features will be limited.{RESET}")

##--------------------------Server Configuration-------------------------##
HEADER = 64
PORT = 5555  # Local port - ply.gg forwards external port 8558 to this
SERVER = "0.0.0.0"  # Bind to all interfaces to accept public connections
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
##------------------------------------------------------------------------##
##--------------Variables for client management----------------##
clients = {}
clients_lock = threading.Lock()
client_id_counter = 0
client_id_lock = threading.Lock()
##------------------------------------------------------------##

##--------------Hash Discovery Variables----------------------##
CRACKED_PATTERNS = {}  # {task_id: pattern}
DB_FILE = "crypto_research.db"
task_broker = None  # Will be initialized if Celery is available
##------------------------------------------------------------##


##--------------------------Server Setup---------------------------------##
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
##------------------------------------------------------------------------##

def send_message(conn, message_data):
    """Send a message with length-prefixed protocol"""
    try:
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

def handle_client(conn, addr):
    global client_id_counter
    client_name = None
    client_id = None
    system_info = None
    
    try:
        with client_id_lock:
            client_id_counter += 1
            client_id = client_id_counter
        
        # Receive client name
        name_length = conn.recv(HEADER).decode(FORMAT)
        if name_length:
            name_length = int(name_length.strip())
            client_name = conn.recv(name_length).decode(FORMAT)
            
            # Receive system info - ensure we receive ALL bytes
            system_info_length = conn.recv(HEADER).decode(FORMAT)
            if system_info_length:
                system_info_length = int(system_info_length.strip())
                
                # Receive all system info data (may come in chunks)
                system_info_data = b""
                while len(system_info_data) < system_info_length:
                    chunk = conn.recv(min(4096, system_info_length - len(system_info_data)))
                    if not chunk:
                        break
                    system_info_data += chunk
                
                system_info_json = system_info_data.decode(FORMAT)
                system_info = json.loads(system_info_json)
            
            with clients_lock:
                clients[addr] = {
                    "conn": conn, 
                    "name": client_name,
                    "id": client_id,
                    "cpu": system_info.get("cpu", "Unknown") if system_info else "Unknown",
                    "cpu_rating": system_info.get("cpu_rating", 0) if system_info else 0,
                    "gpu": system_info.get("gpu", {}) if system_info else {},
                    "gpu_rating": system_info.get("gpu", {}).get("rating", 0) if system_info else 0
                }
            
            cpu_info = system_info.get("cpu", "Unknown") if system_info else "Unknown"
            cpu_rating = system_info.get("cpu_rating", 0) if system_info else 0
            gpu_info = system_info.get("gpu", {}) if system_info else {}
            gpu_name = gpu_info.get("name", "Unknown") if isinstance(gpu_info, dict) else "Unknown"
            gpu_memory = gpu_info.get("memory_total", "N/A") if isinstance(gpu_info, dict) else "N/A"
            gpu_rating = gpu_info.get("rating", 0) if isinstance(gpu_info, dict) else 0
            
            # Create rating bar
            def get_rating_bar(rating):
                filled = "█" * rating
                empty = "░" * (10 - rating)
                return f"{filled}{empty}"
            
            print(f"\n{GREEN}┌{'─'*78}┐{RESET}")
            print(f"{GREEN}│{RESET} {BLUE}✓ NEW CLIENT CONNECTED{RESET}                                                    {GREEN}│{RESET}")
            print(f"{GREEN}├{'─'*78}┤{RESET}")
            print(f"{GREEN}│{RESET}   Client ID:   {YELLOW}#{client_id:<59}{RESET} {GREEN}│{RESET}")
            print(f"{GREEN}│{RESET}   Client Name: {YELLOW}{client_name:<60}{RESET} {GREEN}│{RESET}")
            print(f"{GREEN}│{RESET}   IP Address:  {YELLOW}{addr[0]:<60}{RESET} {GREEN}│{RESET}")
            print(f"{GREEN}│{RESET}   Port:        {YELLOW}{addr[1]:<60}{RESET} {GREEN}│{RESET}")
            print(f"{GREEN}├{'─'*78}┤{RESET}")
            print(f"{GREEN}│{RESET} {BLUE}System Information:{RESET}                                                      {GREEN}│{RESET}")
            
            # Handle long CPU names
            if len(cpu_info) > 50:
                cpu_display = cpu_info[:47] + "..."
            else:
                cpu_display = cpu_info
            cpu_rating_bar = get_rating_bar(cpu_rating)
            padding = 54 - len(cpu_display)
            print(f"{GREEN}│{RESET}   CPU: {YELLOW}{cpu_display}{' ' * padding}{RESET} [{cpu_rating_bar}] {cpu_rating}/10 {GREEN}│{RESET}")
            
            # Handle long GPU names
            if len(gpu_name) > 50:
                gpu_display = gpu_name[:47] + "..."
            else:
                gpu_display = gpu_name
            gpu_rating_bar = get_rating_bar(gpu_rating)
            padding = 54 - len(gpu_display)
            print(f"{GREEN}│{RESET}   GPU: {YELLOW}{gpu_display}{' ' * padding}{RESET} [{gpu_rating_bar}] {gpu_rating}/10 {GREEN}│{RESET}")
            
            if gpu_memory != "N/A":
                print(f"{GREEN}│{RESET}   GPU Memory: {YELLOW}{gpu_memory:<57}{RESET} {GREEN}│{RESET}")
            print(f"{GREEN}└{'─'*78}┘{RESET}")
            print(f"{RED}Server> {RESET}", end="", flush=True)
            
            connected = True
            while connected:
                try:
                    # Receive header length
                    header_data = conn.recv(HEADER)
                    if not header_data:
                        connected = False
                        break
                    
                    message_length = int(header_data.decode(FORMAT).strip())
                    
                    # Receive the actual message
                    message_data = b''
                    while len(message_data) < message_length:
                        chunk = conn.recv(min(4096, message_length - len(message_data)))
                        if not chunk:
                            connected = False
                            break
                        message_data += chunk
                    
                    if not connected:
                        break
                    
                    # Parse the message
                    try:
                        message = json.loads(message_data.decode(FORMAT))
                        
                        # Handle WORKER_ID messages from clients after broadcast
                        if message.get("type") == "WORKER_ID":
                            worker_id = message.get("worker_id")
                            if worker_id:
                                with clients_lock:
                                    if addr in clients:
                                        clients[addr]["worker_id"] = worker_id
                                        clients[addr]["worker_status"] = "STARTING"
                                print(f"\n{GREEN}[WORKER] {client_name} registered as {YELLOW}{worker_id}{RESET}")
                                print(f"{RED}Server> {RESET}", end="", flush=True)
                        
                        # Handle STATUS messages from workers (socket_client)
                        elif message.get("type") == "STATUS":
                            worker_id = message.get("worker_id") or message.get("client_id")
                            status = message.get("status")
                            if worker_id:
                                with clients_lock:
                                    if addr in clients:
                                        clients[addr]["worker_id"] = worker_id
                                        clients[addr]["worker_status"] = status
                                print(f"\n{BLUE}[WORKER] {worker_id} status: {status}{RESET}")
                                print(f"{RED}Server> {RESET}", end="", flush=True)
                        
                        # Handle RESULT messages from workers after brute force
                        elif message.get("type") == "RESULT":
                            worker_id = message.get("worker_id")
                            status = message.get("status")
                            pattern = message.get("pattern")
                            hash_value = message.get("hash", "unknown")
                            
                            if status == "CRACKED":
                                print(f"\n{GREEN}┌{'─'*78}┐{RESET}")
                                print(f"{GREEN}│{RESET} 🎉 PATTERN CRACKED!                                                        {GREEN}│{RESET}")
                                print(f"{GREEN}├{'─'*78}┤{RESET}")
                                print(f"{GREEN}│{RESET}   Worker:   {YELLOW}{worker_id:<60}{RESET} {GREEN}│{RESET}")
                                print(f"{GREEN}│{RESET}   Hash:     {YELLOW}{hash_value:<60}{RESET} {GREEN}│{RESET}")
                                print(f"{GREEN}│{RESET}   Pattern:  {YELLOW}{pattern:<60}{RESET} {GREEN}│{RESET}")
                                print(f"{GREEN}└{'─'*78}┘{RESET}")
                                # Store in CRACKED_PATTERNS
                                CRACKED_PATTERNS[hash_value] = pattern
                            else:
                                print(f"\n{YELLOW}[RESULT] {worker_id} finished - Pattern not found in assigned range{RESET}")
                            print(f"{RED}Server> {RESET}", end="", flush=True)
                        
                        # Handle file_archive messages from clients
                        elif message.get("type") == "file_archive":
                            filename = message.get("filename")
                            base64_data = message.get("data")
                            
                            if filename and base64_data:
                                result = receive_and_decompress_file(base64_data, filename, output_dir="Networking/logs/files")
                                
                                if result['success']:
                                    print(f"\n{GREEN}┌{'─'*78}┐{RESET}")
                                    print(f"{GREEN}│{RESET} {BLUE}✓ FILE RECEIVED FROM CLIENT{RESET}                                         {GREEN}│{RESET}")
                                    print(f"{GREEN}├{'─'*78}┤{RESET}")
                                    print(f"{GREEN}│{RESET}   Client: {YELLOW}{client_name:<60}{RESET} {GREEN}│{RESET}")
                                    print(f"{GREEN}│{RESET}   File:   {YELLOW}{filename:<60}{RESET} {GREEN}│{RESET}")
                                    print(f"{GREEN}│{RESET}   Size:   {YELLOW}{result['original_size']} bytes{' '*(48-len(str(result['original_size'])))}{RESET} {GREEN}│{RESET}")
                                    print(f"{GREEN}│{RESET}   Saved:  {YELLOW}{result['path']:<60}{RESET} {GREEN}│{RESET}")
                                    print(f"{GREEN}└{'─'*78}┘{RESET}")
                                    print(f"{RED}Server> {RESET}", end="", flush=True)
                                else:
                                    print(f"\n{RED}Failed to receive file {filename}: {result['message']}{RESET}")
                                    print(f"{RED}Server> {RESET}", end="", flush=True)
                    
                    except json.JSONDecodeError:
                        pass
                
                except:
                    connected = False
                    
    except Exception as e:
        print(f"{RED}[ERROR] Failed to receive client name from {addr}: {e}{RESET}")
    
    with clients_lock:
        if addr in clients:
            del clients[addr]
    conn.close()

def display_connected_clients():
    client_list = list_clients()
    
    def get_rating_bar(rating):
        filled = "█" * rating
        empty = "░" * (10 - rating)
        return f"{filled}{empty}"
    
    print(f"\n{BLUE}┌{'─'*78}┐{RESET}")
    print(f"{BLUE}│{RESET} 📊 CONNECTED CLIENTS                                                          {BLUE}│{RESET}")
    print(f"{BLUE}├{'─'*78}┤{RESET}")
                
    if client_list:
        for i, (addr, name, client_id, cpu, cpu_rating, gpu, gpu_rating, worker_id, worker_status) in enumerate(client_list, 1):
            # Client basic info - show worker_id if available
            display_id = worker_id if worker_id else f"#{client_id}"
            status_str = f" [{worker_status}]" if worker_status else ""
            print(f"{BLUE}│{RESET}   {YELLOW}[{display_id}]{RESET}{status_str} {GREEN}{name}{RESET} - {YELLOW}{addr[0]}:{addr[1]}{RESET}")
            
            # CPU info with rating
            cpu_display = cpu[:50] if len(cpu) > 50 else cpu
            cpu_rating_bar = get_rating_bar(cpu_rating)
            padding = 54 - len(cpu_display)
            print(f"{BLUE}│{RESET}     CPU: {cpu_display}{' ' * padding} [{cpu_rating_bar}] {cpu_rating}/10 {BLUE}│{RESET}")
            
            # GPU info with rating
            gpu_name = gpu.get("name", "Unknown") if isinstance(gpu, dict) else "Unknown"
            gpu_display = gpu_name[:50] if len(gpu_name) > 50 else gpu_name
            gpu_rating_bar = get_rating_bar(gpu_rating)
            padding = 54 - len(gpu_display)
            print(f"{BLUE}│{RESET}     GPU: {gpu_display}{' ' * padding} [{gpu_rating_bar}] {gpu_rating}/10 {BLUE}│{RESET}")
            
            # GPU memory if available
            if isinstance(gpu, dict) and gpu.get("memory_total") != "N/A":
                gpu_mem = gpu.get("memory_total", "N/A")
                padding = 66 - len(gpu_mem)
                print(f"{BLUE}│{RESET}     Memory: {gpu_mem}{' ' * padding}{BLUE}│{RESET}")
            
            # Add separator between clients if not last
            if i < len(client_list):
                print(f"{BLUE}│{RESET}{' ' * 78}{BLUE}│{RESET}")
    else:
        print(f"{BLUE}│{RESET}   {YELLOW}No clients connected{RESET}                                                   {BLUE}│{RESET}")
                
    print(f"{BLUE}├{'─'*78}┤{RESET}")
    print(f"{BLUE}│{RESET}   • Total clients: {len(client_list):<56}{BLUE}│{RESET}")
    print(f"{BLUE}│{RESET}   • Server address: {SERVER}:{PORT:<53}{BLUE}│{RESET}")
    print(f"{BLUE}└{'─'*78}┘{RESET}")


def list_clients():
    with clients_lock:
        return [(addr, info["name"], info["id"], info.get("cpu", "Unknown"), info.get("cpu_rating", 0), info.get("gpu", {}), info.get("gpu_rating", 0), info.get("worker_id", None), info.get("worker_status", None)) for addr, info in clients.items()]
def disconnect_client_by_id(client_id):
    with clients_lock:
        addr_to_remove = None
        for addr, info in clients.items():
            if info["id"] == client_id:
                try:
                    info["conn"].close()
                    addr_to_remove = addr
                    print(f"{GREEN} Client ID #{client_id} ({info['name']}) disconnected successfully.{RESET}")
                except Exception as e:
                    print(f"{RED} Error disconnecting client #{client_id}: {e}{RESET}")
                    return False
                break
        
        if addr_to_remove:
            del clients[addr_to_remove]
            return True
    
    print(f"{YELLOW}Client ID #{client_id} not found.{RESET}")
    return False

def disconnect_all_clients():
    with clients_lock:
        if not clients:
            print(f"{YELLOW} No clients connected.{RESET}")
            return
        
        disconnected = 0
        total = len(clients)
        addrs_to_remove = []
        
        for addr, info in list(clients.items()):
            try:
                info["conn"].close()
                addrs_to_remove.append(addr)
                disconnected += 1
            except Exception as e:
                print(f"{RED}Error disconnecting {info['name']}: {e}{RESET}")
        
        # Remove all disconnected clients from the dictionary
        for addr in addrs_to_remove:
            del clients[addr]
        
        print(f"{GREEN}Disconnected {disconnected}/{total} clients.{RESET}")




def PrintBanner():

    def clear_terminal():
        import os
        os.system('cls' if os.name == 'nt' else 'clear')

    clear_terminal()
    print(RED + "\n" + "╔" + "═"*78 + "╗")
    print("║" + " "*20 + "DISTRIBUTED PASSWORD TESTING SERVER" + " "*23 + "║")
    print("╚" + "═"*78 + "╝")
    print("\n📋 Available Commands:")
    print("  ┌─────────────────────────────────────────────────────────────────────────┐")
    print("  │ Client Management:                                                      │")
    print("  │   list              - List all connected clients                        │")
    print("  │   send <ip>         - Send password testing task to specific client     │")
    print("  │   broadcast         - Send task to all connected clients                │")
    print("  │   send file         - Send file to all connected clients                │")
    print("  │   send file <ip>    - Send file to a specific client                    │")
    print("  │   disconnect <ip>   - Disconnect specific client                        │")
    print("  │   disconnect all    - Disconnect all clients                            │")
    print("  │                                                                         │")
    print("  │ Hash Discovery (Distributed Brute Force Offline):                       │")
    print("  │   hash add          - Add a research entry (Pattern -> MD5)             │")
    print("  │   hash list         - View all research entries in database             │")
    print("  │   hash crack        - Start distributed pattern search                  │")
    print("  │   hash status       - Show cracked patterns and task status             │")
    print("  │                                                                         │")
    print("  │ Utility:                                                                │")
    print("  │   clear             - Clear the terminal screen                         │")
    print("  │   help              - Show this help message                            │")
    print("  │   status            - Show server status and statistics                 │")
    print("  │   logs              - Show recent client logs                           │")
    print("  │   quit              - Shut down the server                              │")
    print("  └─────────────────────────────────────────────────────────────────────────┘")
    celery_status = f"{GREEN}Available{RESET}" if CELERY_AVAILABLE else f"{RED}Not Available{RESET}"
    print(f"  Celery Status: {celery_status}")
    print("" + RESET)

def select_file_dialog():
    
    root = Tk()
    root.withdraw()  
    root.attributes('-topmost', True) # avance le window vers le front
    
    file_path = filedialog.askopenfilename(
        title="Select file to send",
        filetypes=[("All files", "*.*")]
    )
    
    root.destroy()
    return file_path if file_path else None


def send_file_to_clients(file_path, target_ip=None):
    try:
        if not file_path or not os.path.exists(file_path):
            print(f"{RED}File not found: {file_path}{RESET}")
            return
        
        filename = os.path.basename(file_path)
        print(f"\n{BLUE}[*] Encoding file: {filename}...{RESET}")
        # code the file to base64 and compress it
        base64_files = files_to_base64_archive([file_path])
        
        if not base64_files:
            print(f"{RED}Failed to encode file{RESET}")
            return
        
        encoded_data = base64_files[filename]
        message = json.dumps({"type": "file_archive", "filename": filename, "data": encoded_data})
        
        if target_ip is None:
            with clients_lock:
                if not clients:
                    print(f"{YELLOW}No clients connected.{RESET}")
                    return
                
                total_clients = len(clients)
                sent_count = 0
                failed_clients = []
                
                for addr, info in clients.items():
                    try:
                        if send_message(info["conn"], message):
                            sent_count += 1
                        else:
                            failed_clients.append(f"{info['name']} ({addr[0]})")
                    except Exception as e:
                        failed_clients.append(f"{info['name']} ({addr[0]}): {str(e)}")
            
            print(f"\n{GREEN}┌{'─'*78}┐{RESET}")
            print(f"{GREEN}│{RESET} {BLUE}✓ FILES BROADCAST COMPLETE{RESET}                                              {GREEN}│{RESET}")
            print(f"{GREEN}├{'─'*78}┤{RESET}")
            print(f"{GREEN}│{RESET}   File:    {YELLOW}{filename:<60}{RESET} {GREEN}│{RESET}")
            print(f"{GREEN}│{RESET}   Sent to: {YELLOW}{sent_count}/{total_clients} clients{' '*(48-len(str(sent_count))-len(str(total_clients)))}{RESET} {GREEN}│{RESET}")
            
            if failed_clients:
                print(f"{GREEN}│{RESET}   Failed:  {RED}{len(failed_clients)} clients{' '*(48)}{GREEN}│{RESET}")
                for failed in failed_clients[:3]:
                    padding = 64 - len(failed)
                    print(f"{GREEN}│{RESET}     - {RED}{failed}{' '*padding}{GREEN}│{RESET}")
                if len(failed_clients) > 3:
                    print(f"{GREEN}│{RESET}     - {RED}... and {len(failed_clients)-3} more{' '*(36)}{GREEN}│{RESET}")
            
            print(f"{GREEN}└{'─'*78}┘{RESET}")
            print(f"{RED}Server> {RESET}", end="", flush=True)
        
        else:
            # Send to specific client
            with clients_lock:
                target_client = None
                client_name = None
                for addr, info in clients.items():
                    if addr[0] == target_ip:
                        target_client = info
                        client_name = info['name']
                        break
                
                if not target_client:
                    print(f"{YELLOW}Client with IP {target_ip} not found.{RESET}")
                    print(f"{RED}Server> {RESET}", end="", flush=True)
                    return
                
                try:
                    if send_message(target_client["conn"], message):
                        print(f"\n{GREEN}┌{'─'*78}┐{RESET}")
                        print(f"{GREEN}│{RESET} {BLUE}✓ FILE SENT SUCCESSFULLY{RESET}                                                {GREEN}│{RESET}")
                        print(f"{GREEN}├{'─'*78}┤{RESET}")
                        print(f"{GREEN}│{RESET}   Client: {YELLOW}{client_name:<60}{RESET} {GREEN}│{RESET}")
                        print(f"{GREEN}│{RESET}   IP:     {YELLOW}{target_ip:<60}{RESET} {GREEN}│{RESET}")
                        print(f"{GREEN}│{RESET}   File:   {YELLOW}{filename:<60}{RESET} {GREEN}│{RESET}")
                        print(f"{GREEN}└{'─'*78}┘{RESET}")
                    else:
                        print(f"{RED}Failed to send file to {client_name} ({target_ip}){RESET}")
                except Exception as e:
                    print(f"{RED}Error sending file to {target_ip}: {e}{RESET}")
                
                print(f"{RED}Server> {RESET}", end="", flush=True)
    
    except Exception as e:
        print(f"{RED}Error sending file: {e}{RESET}")
        print(f"{RED}Server> {RESET}", end="", flush=True)

def start():
    try:
        server.listen()
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"\n[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
            print(f"{RED}Server> {RESET}", end="", flush=True)
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt detected. Shutting down the server...")
    finally:
        server.close()


def broadcating_BrutForcing():
    # First, get the hash list and let user select one
    db = ResearchDBManager()
    entries = db.get_all_entries()
    
    if not entries:
        print(f"{YELLOW}No hash entries found in database. Use 'hash add' to add entries first.{RESET}")
        return
    
    # Display available hashes
    print(f"\n{BLUE}┌{'─'*78}┐{RESET}")
    print(f"{BLUE}│{RESET} 📋 SELECT A HASH TO BROADCAST                                              {BLUE}│{RESET}")
    print(f"{BLUE}├{'─'*78}┤{RESET}")
    
    for i, (entry_id, encrypted) in enumerate(entries, 1):
        print(f"{BLUE}│{RESET}   [{YELLOW}{i}{RESET}] {GREEN}{entry_id:<20}{RESET} -> {YELLOW}{encrypted}{RESET}")
    
    print(f"{BLUE}└{'─'*78}┘{RESET}")
    
    # Get user selection
    try:
        selection = input(f"{BLUE}Enter the number of the hash to broadcast (1-{len(entries)}): {RESET}").strip()
        selection_idx = int(selection) - 1
        
        if selection_idx < 0 or selection_idx >= len(entries):
            print(f"{RED}Invalid selection. Please enter a number between 1 and {len(entries)}.{RESET}")
            return
        
        selected_entry_id, selected_hash = entries[selection_idx]
        print(f"\n{GREEN}Selected hash: {selected_hash} (Entry: {selected_entry_id}){RESET}")
        
    except ValueError:
        print(f"{RED}Invalid input. Please enter a valid number.{RESET}")
        return
    
    # Broadcast the selected hash to all clients
    with clients_lock:
        try:
            broadcast_data = json.dumps({
                "type": "BROADCASTING",
                "hash_value": selected_hash,
                "entry_id": selected_entry_id
            })
            
            sent_count = 0
            for addr, info in clients.items():
                if send_message(info["conn"], broadcast_data):
                    sent_count += 1
            
            print(f"{GREEN}Broadcast sent to {sent_count}/{len(clients)} clients with hash: {selected_hash[:16]}...{RESET}")

        except Exception as e:
            print(f"{RED}Error broadcasting brute force message: {e}{RESET}")


##--------------------------Hash Discovery Functions--------------------------##

class ResearchDBManager:
    """Manages the local SQLite database for research entry storage."""
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.cur = self.conn.cursor()
        self.create_research_table()

    def create_research_table(self):
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS research_entries (
                entry_id TEXT PRIMARY KEY,
                encrypted_pattern TEXT
            )
        """)
        self.conn.commit()

    def add_research_entry(self, entry_id, pattern_data):
        # NOTE: Using MD5 for hashing as per user's original code
        encrypted = hashlib.md5(pattern_data.encode()).hexdigest()
        self.cur.execute("INSERT OR REPLACE INTO research_entries VALUES (?,?)", 
                         (entry_id, encrypted))
        self.conn.commit()
        return encrypted

    def get_entry_encryption(self, entry_id):
        self.cur.execute("SELECT encrypted_pattern FROM research_entries WHERE entry_id=?", (entry_id,))
        row = self.cur.fetchone()
        return row[0] if row else None
    
    def get_all_entries(self):
        self.cur.execute("SELECT entry_id, encrypted_pattern FROM research_entries")
        return self.cur.fetchall()


class TaskBroker(threading.Thread):
    """
    Pulls packaged tasks from the Celery Backend and distributes them to 
    available socket clients.
    """
    
    def __init__(self, client_data_ref, client_lock_ref=None):
        super().__init__()
        self.running = True
        self.polling_interval = 0.5
        self.client_data_ref = client_data_ref 
        self.client_lock = client_lock_ref or clients_lock
        self.task_groups = {}  # {group_id: list_of_task_ids}

    def _get_idle_client_info(self):
        """Finds an IDLE client."""
        with self.client_lock:
            for addr, info in self.client_data_ref.items():
                status = info.get("worker_status", "IDLE")
                if status == "IDLE" and info.get("conn") is not None:
                    return addr, info["conn"], info.get("name", f"Client-{addr[1]}")
        return None, None, None

    def _set_client_status(self, addr, status):
        """Updates the client status in the main server's dictionary."""
        with self.client_lock:
            if addr in self.client_data_ref:
                self.client_data_ref[addr]["worker_status"] = status
                
    def _send_task_message(self, conn, message_data):
        """Sends a JSON message over the socket using newline delimiter."""
        try:
            conn.sendall((json.dumps(message_data) + '\n').encode('utf-8'))
            return True
        except Exception:
            return False

    def _get_next_available_task_id(self):
        """Pulls the next available task ID from any active group."""
        for group_id, task_list in self.task_groups.items():
            if task_list:
                return group_id, task_list.pop(0)
        return None, None
        
    def run(self):
        if not CELERY_AVAILABLE:
            print(f"{YELLOW}[TASK BROKER] Celery not available. Broker thread exiting.{RESET}")
            return
            
        from celery.result import AsyncResult
        from OFFLINE_bruteforce.Mohamed.socket_tasks import app as celery_app
        
        print(f"[{time.strftime('%H:%M:%S')}] [TASK BROKER] Starting up. Polling Celery Backend...")
        
        while self.running:
            addr, conn, name = self._get_idle_client_info()
            group_id, task_id = self._get_next_available_task_id()

            if conn and task_id:
                try:
                    task_result = AsyncResult(task_id, app=celery_app)
                    payload_dict = task_result.get(timeout=3) 
                    
                    if not isinstance(payload_dict, dict) or payload_dict.get('type') != 'MD5_BRUTE_FORCE_CHUNK':
                        print(f"[{time.strftime('%H:%M:%S')}] [BROKER WARNING] Task {task_id[:8]}... returned invalid payload. Skipping.")
                        continue

                    self._set_client_status(addr, "BUSY") 

                    print(f"[{time.strftime('%H:%M:%S')}] [BROKER] Sending task {task_id[:8]}... to {name}.")
                    if self._send_task_message(conn, payload_dict):
                        pass  # Success
                    else:
                        self.task_groups[group_id].insert(0, task_id) 
                        self._set_client_status(addr, "IDLE") 
                        print(f"[{time.strftime('%H:%M:%S')}] [BROKER ERROR] Failed to send task to {name}. Re-queued.")

                except Exception as e:
                    print(f"[{time.strftime('%H:%M:%S')}] [BROKER ERROR] Failed to fetch or process Celery task {task_id}: {e}. Re-queuing.")
                    if group_id in self.task_groups:
                        self.task_groups[group_id].insert(0, task_id) 
                    self._set_client_status(addr, "IDLE") 
            
            time.sleep(self.polling_interval)

    def enqueue_group_tasks(self, group_id, num_tasks):
        """
        Fetches all task IDs belonging to a Celery group and adds them to the queue.
        """
        if not CELERY_AVAILABLE:
            print(f"{RED}[BROKER] Celery not available.{RESET}")
            return
            
        from celery.result import AsyncResult
        from OFFLINE_bruteforce.Mohamed.socket_tasks import app as celery_app
        
        start_time = time.time()
        try:
            group_result = AsyncResult(group_id, app=celery_app)
            
            while not group_result.ready() and (time.time() - start_time) < 5:
                 time.sleep(0.1)
            
            task_ids = [r.id for r in group_result.children]

            if len(task_ids) != num_tasks:
                print(f"[{time.strftime('%H:%M:%S')}] [BROKER WARNING] Expected {num_tasks} tasks, found {len(task_ids)}. Adding what was found.")

            self.task_groups[group_id] = task_ids
            print(f"[{time.strftime('%H:%M:%S')}] [TASK BROKER] New task group {group_id[:8]}... received: {len(task_ids)} added to queue.")
            
        except Exception as e:
            print(f"[{time.strftime('%H:%M:%S')}] [BROKER FATAL] Could not retrieve task IDs from group {group_id}: {e}")
            
    def stop(self):
        self.running = False
        print(f"[{time.strftime('%H:%M:%S')}] [TASK BROKER] Shutting down.")


def get_task_splitting_prefixes(length, num_workers, char_set_size):
    """
    SMART ALGORITHM: Calculates the best prefix length to split the work 
    to ensure all 'num_workers' are kept busy.
    """
    if not CELERY_AVAILABLE:
        return [None]
        
    if length <= 2 or char_set_size ** length <= num_workers:
        return [None]

    required_prefix_len = math.ceil(math.log(num_workers) / math.log(char_set_size))
    prefix_len = min(int(required_prefix_len), length)

    if prefix_len == 0:
        return [None]

    prefixes = ["".join(p) for p in itertools.product(CHARACTER_SET, repeat=prefix_len)]
    return prefixes


def discover_pattern_distributed(entry_id, num_workers, db_manager):
    """
    Splits the search space and dispatches task PACKAGES to Celery.
    """
    if not CELERY_AVAILABLE:
        print(f"{RED}Celery is not available. Cannot run distributed discovery.{RESET}")
        return None, 0
        
    target_encryption = db_manager.get_entry_encryption(entry_id)
    if target_encryption is None:
        print(f"{RED}Research entry '{entry_id}' not found in database.{RESET}")
        return None, 0

    char_set_size = len(CHARACTER_SET)
    
    print(f"\n{BLUE}🔍 DISTRIBUTING PATTERN DISCOVERY for: {entry_id}{RESET}")
    print(f"Target encryption: {YELLOW}{target_encryption}{RESET}")

    task_signatures = []
    total_tasks_submitted = 0

    for length in range(1, MAX_PATTERN_LENGTH + 1):
        prefixes = get_task_splitting_prefixes(length, num_workers, char_set_size)
        
        print(f"  - Length {length}: Smartly splitting into {len(prefixes)} task(s).")
        
        for prefix in prefixes:
            task_signatures.append(
                package_socket_task.s(target_encryption, length, prefix)
            )
        total_tasks_submitted += len(prefixes)
    
    if not task_signatures:
         print(f"{RED}No tasks generated. Check MAX_PATTERN_LENGTH and CHARACTER_SET settings.{RESET}")
         return None, 0
         
    print(f"\nSubmitting a total of {GREEN}**{total_tasks_submitted}**{RESET} task PACKAGES to the distributed queue...")
    
    job = chord(
        group(task_signatures), 
        callback=handle_completion_callback.s()
    )
    
    job_result = job.apply_async() 
    print(f"Job submitted. Celery Job ID: {YELLOW}{job_result.id}{RESET}")
    
    return job_result.parent.id, total_tasks_submitted


def hash_add_entry():
    """Add a new research entry to the database."""
    db = ResearchDBManager()
    entry_id = input(f"{BLUE}Research entry ID: {RESET}").strip()
    if not entry_id:
        print(f"{YELLOW}Entry ID cannot be empty.{RESET}")
        return
    pattern_data = input(f"{BLUE}Pattern data to encrypt (the original text): {RESET}").strip()
    if not pattern_data:
        print(f"{YELLOW}Pattern data cannot be empty.{RESET}")
        return
    encrypted = db.add_research_entry(entry_id, pattern_data)
    print(f"{GREEN}Research entry added successfully.{RESET}")
    print(f"  Entry ID: {YELLOW}{entry_id}{RESET}")
    print(f"  MD5 Hash: {YELLOW}{encrypted}{RESET}")


def hash_list_entries():
    """List all research entries in the database."""
    db = ResearchDBManager()
    entries = db.get_all_entries()
    
    print(f"\n{BLUE}┌{'─'*78}┐{RESET}")
    print(f"{BLUE}│{RESET} 📊 RESEARCH ENTRIES IN DATABASE                                           {BLUE}│{RESET}")
    print(f"{BLUE}├{'─'*78}┤{RESET}")
    
    if entries:
        for entry_id, encrypted in entries:
            print(f"{BLUE}│{RESET}   {YELLOW}{entry_id:<20}{RESET} -> {GREEN}{encrypted}{RESET}")
    else:
        print(f"{BLUE}│{RESET}   {YELLOW}No research entries found.{RESET}")
    
    print(f"{BLUE}└{'─'*78}┘{RESET}")


def hash_crack():
    """Start distributed pattern discovery."""
    global task_broker
    
    if not CELERY_AVAILABLE:
        print(f"{RED}Celery is not available. Install celery and redis to use this feature.{RESET}")
        return
    
    db = ResearchDBManager()
    
    # Get number of workers
    try:
        with clients_lock:
            connected_count = len(clients)
        
        default_workers = max(connected_count, 1)
        workers_input = input(f"{BLUE}Enter the number of available workers [{default_workers}]: {RESET}").strip()
        num_workers = int(workers_input) if workers_input else default_workers
        
        if num_workers <= 0:
            raise ValueError
    except ValueError:
        print(f"{RED}Invalid number of workers. Please enter a positive integer.{RESET}")
        return
    
    # Get entry ID
    entry_id = input(f"{BLUE}Research entry ID to analyze: {RESET}").strip()
    if not entry_id:
        print(f"{YELLOW}Entry ID cannot be empty.{RESET}")
        return
    
    # Run distributed discovery
    group_id, num_tasks = discover_pattern_distributed(entry_id, num_workers, db)
    
    if group_id and task_broker:
        print(f"[{time.strftime('%H:%M:%S')}] Notifying TaskBroker of {num_tasks} new tasks...")
        task_broker.enqueue_group_tasks(group_id, num_tasks)


def hash_status():
    """Show status of cracked patterns and pending tasks."""
    global task_broker, CRACKED_PATTERNS
    
    print(f"\n{BLUE}┌{'─'*78}┐{RESET}")
    print(f"{BLUE}│{RESET} 📊 HASH DISCOVERY STATUS                                                   {BLUE}│{RESET}")
    print(f"{BLUE}├{'─'*78}┤{RESET}")
    
    # Show Celery status
    celery_status = f"{GREEN}Available{RESET}" if CELERY_AVAILABLE else f"{RED}Not Available{RESET}"
    print(f"{BLUE}│{RESET}   Celery Status: {celery_status}")
    
    # Show broker status
    if task_broker:
        pending_tasks = sum(len(tasks) for tasks in task_broker.task_groups.values())
        print(f"{BLUE}│{RESET}   Task Broker: {GREEN}Running{RESET}")
        print(f"{BLUE}│{RESET}   Pending Tasks: {YELLOW}{pending_tasks}{RESET}")
    else:
        print(f"{BLUE}│{RESET}   Task Broker: {RED}Not Started{RESET}")
    
    print(f"{BLUE}├{'─'*78}┤{RESET}")
    print(f"{BLUE}│{RESET} 🎉 CRACKED PATTERNS                                                        {BLUE}│{RESET}")
    print(f"{BLUE}├{'─'*78}┤{RESET}")
    
    if CRACKED_PATTERNS:
        for task_id, pattern in CRACKED_PATTERNS.items():
            print(f"{BLUE}│{RESET}   Task {YELLOW}{task_id[:8]}...{RESET} -> {GREEN}{pattern}{RESET}")
    else:
        print(f"{BLUE}│{RESET}   {YELLOW}No patterns cracked yet.{RESET}")
    
    print(f"{BLUE}└{'─'*78}┘{RESET}")

##----------------------------------------------------------------------------##

def interactive_terminal():
    global task_broker
    
    # Start the TaskBroker if Celery is available
    if CELERY_AVAILABLE:
        task_broker = TaskBroker(clients, clients_lock)
        task_broker.daemon = True
        task_broker.start()
        print(f"{GREEN}[TASK BROKER] Started successfully.{RESET}")
    
    try:
        while True:
            print(f"{RED}Server> {RESET}", end="", flush=True)
            command = input().strip().lower()
            
            if command == "help":
                PrintBanner()
            elif command == "list":
                display_connected_clients()
            elif command.startswith("disconnect "):
                args = command.split(maxsplit=1)
                if len(args) < 2:
                    print(f"{YELLOW}Usage: disconnect <id|ip|all>{RESET}")
                else:
                    target = args[1].strip()
                    if target == "all":
                        disconnect_all_clients()
                    elif target.startswith("#"):
                        try:
                            client_id = int(target[1:])
                            disconnect_client_by_id(client_id)
                        except ValueError:
                            print(f"{YELLOW} Invalid client ID. Use format: Example disconnect #1{RESET}")
                    else:
                        try:
                            client_id = int(target)
                            disconnect_client_by_id(client_id)
                        except ValueError:
                            print(f"{YELLOW}Invalid input. Use: disconnect <id>, disconnect <ip>, or disconnect all{RESET}")
            elif command == "clear" or command == "cls":
                clear_terminal()
                PrintBanner()
            elif command == "status":
                print(f"[STATUS] Active connections: {threading.active_count() - 1}")
                with clients_lock:
                    print(f"[STATUS] Connected clients: {len(clients)}")
                if task_broker:
                    pending = sum(len(tasks) for tasks in task_broker.task_groups.values())
                    print(f"[STATUS] Pending tasks: {pending}")
            elif command == "logs":
                print(f"{YELLOW}[LOGS] Feature not implemented yet.{RESET}")
            elif command == "quit":
                print(f"{RED} Shutting down the server...{RESET}")
                if task_broker:
                    task_broker.stop()
                os._exit(0)
            elif command.startswith("send file"):
                args = command.split(maxsplit=2)
                target_ip = args[2].strip() if len(args) >= 3 else None
                
                file_path = select_file_dialog()
                
                if file_path:
                    send_thread = threading.Thread(target=send_file_to_clients, args=(file_path, target_ip), daemon=True)
                    send_thread.start()
                else:
                    print(f"{YELLOW}No file selected.{RESET}")
            elif command == "broadcast":
                broadcating_BrutForcing()
            
            # Hash Discovery Commands
            elif command == "hash add":
                hash_add_entry()
            elif command == "hash list":
                hash_list_entries()
            elif command == "hash crack":
                hash_crack()
            elif command == "hash status":
                hash_status()
            elif command.startswith("hash"):
                print(f"{YELLOW}Unknown hash command. Available: hash add, hash list, hash crack, hash status{RESET}")
            elif command == "":
                pass  # Empty command, do nothing
            else:
                print(f"{YELLOW}Unknown command: '{command}'. Type 'help' for available commands.{RESET}")
                
    except KeyboardInterrupt:
        print("\nDisconnecting from server...")
        if task_broker:
            task_broker.stop()
        server.close()
        print("Connection closed.")
    except Exception as e:
        print(f"An error occurred: {e}")
        if task_broker:
            task_broker.stop()
        if 'server' in locals():
            server.close()



def clear_terminal():
    os.system('clear' if os.name == 'posix' else 'cls')

if __name__ == "__main__":
    PrintBanner()
    server_thread = threading.Thread(target=start, daemon=True)
    server_thread.start()
    interactive_terminal()
