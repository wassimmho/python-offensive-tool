import socket
import threading
import os
import json
import time
from Function_Net.sending import files_to_base64, base64_to_file, files_to_base64_archive, base64_archive_to_files, selecting_files
from Function_Net.recieving import receive_and_decompress_file, receive_multiple_files, receive_file_simple
from tkinter import Tk, filedialog

##--------------------------Server Configuration-------------------------##
HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
##------------------------------------------------------------------------##


##--------------------------ANSI escape codes-----------------------------##
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
##------------------------------------------------------------------------##
##--------------Variables for client management----------------##
clients = {}
clients_lock = threading.Lock()
client_id_counter = 0
client_id_lock = threading.Lock()
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
            
            # Receive system info
            system_info_length = conn.recv(HEADER).decode(FORMAT)
            if system_info_length:
                system_info_length = int(system_info_length.strip())
                system_info_json = conn.recv(system_info_length).decode(FORMAT)
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
                        
                        # Handle file_archive messages from clients
                        if message.get("type") == "file_archive":
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
        for i, (addr, name, client_id, cpu, cpu_rating, gpu, gpu_rating) in enumerate(client_list, 1):
            # Client basic info
            print(f"{BLUE}│{RESET}   {YELLOW}[ID: #{client_id}]{RESET} {GREEN}{name}{RESET} - {YELLOW}{addr[0]}:{addr[1]}{RESET}")
            
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
        return [(addr, info["name"], info["id"], info.get("cpu", "Unknown"), info.get("cpu_rating", 0), info.get("gpu", {}), info.get("gpu_rating", 0)) for addr, info in clients.items()]
def disconnect_client_by_id(client_id):
    with clients_lock:
        for addr, info in clients.items():
            if info["id"] == client_id:
                try:
                    info["conn"].close()
                    print(f"{GREEN} Client ID #{client_id} ({info['name']}) disconnected successfully.{RESET}")
                    return True
                except Exception as e:
                    print(f"{RED} Error disconnecting client #{client_id}: {e}{RESET}")
                    return False
    print(f"{YELLOW}Client ID #{client_id} not found.{RESET}")
    return False

def disconnect_all_clients():
    with clients_lock:
        if not clients:
            print(f"{YELLOW} No clients connected.{RESET}")
            return
        
        disconnected = 0
        total = len(clients)
        
        for addr, info in list(clients.items()):
            try:
                info["conn"].close()
                disconnected += 1
            except Exception as e:
                print(f"{RED}Error disconnecting {info['name']}: {e}{RESET}")
        
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
    print("  │ Utility:                                                                │")
    print("  │   clear             - Clear the terminal screen                         │")
    print("  │   help              - Show this help message                            │")
    print("  │   status            - Show server status and statistics                 │")
    print("  │   logs              - Show recent client logs                           │")
    print("  │   quit              - Shut down the server                              │")
    print("  └─────────────────────────────────────────────────────────────────────────┘")
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
        PrintBanner()
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt detected. Shutting down the server...")
    finally:
        server.close()


def broadcating_BrutForcing():
    with clients_lock:
        try:
            for addr, info in clients.items():
                 send_message(info["conn"], "BROADCASTING")

        except Exception as e:
            print(f"{RED}Error broadcasting brute force message: {e}{RESET}")

def interactive_terminal():
    try:
        while True:
            print(f"{RED}Server> {RESET}", end="")
            command = input().strip()
            
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
            elif command == "logs":
                print(f"{YELLOW}[LOGS] Feature not implemented yet.{RESET}")
            elif command == "quit":
                print(f"{RED} Shutting down the server...{RESET}")
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
    except KeyboardInterrupt:
        print("\nDisconnecting from server...")
        server.close()
        print("Connection closed.")
    except Exception as e:
        print(f"An error occurred: {e}")
        if 'server' in locals():
            server.close()



def clear_terminal():
    os.system('clear' if os.name == 'posix' else 'cls')

if __name__ == "__main__":
    PrintBanner()
    server_thread = threading.Thread(target=start, daemon=True)
    server_thread.start()
    interactive_terminal()
