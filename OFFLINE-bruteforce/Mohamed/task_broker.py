# task_broker.py (The thread that manages task distribution to clients)

import threading
import time
import json
from celery.result import AsyncResult
from Mohamed.socket_tasks import app as celery_app 
from Mohamed.config import CELERY_RESULT_BACKEND

# Global client connection state managed by main_server.py
CLIENT_CONNECTIONS = {} 
client_status_lock = threading.Lock() 

class TaskBroker(threading.Thread):
    """
    Pulls packaged tasks from the Celery Backend and distributes them to 
    available socket clients.
    """
    
    def __init__(self, client_data_ref):
        super().__init__()
        self.running = True
        self.polling_interval = 0.5
        # client_data_ref is a reference to the global CLIENT_CONNECTIONS dict in main_server.py
        self.client_data_ref = client_data_ref 
        self.task_groups = {} # {group_id: list_of_task_ids}

    def _get_idle_client_info(self):
        """Finds an IDLE client."""
        with client_status_lock:
            for addr, info in self.client_data_ref.items():
                # Must be IDLE and have a valid connection object
                if info.get("status") == "IDLE" and info.get("conn") is not None:
                    return addr, info["conn"], info["name"]
        return None, None, None

    def _set_client_status(self, addr, status):
        """Updates the client status in the main server's dictionary."""
        with client_status_lock:
            if addr in self.client_data_ref:
                self.client_data_ref[addr]["status"] = status
                
    def _send_message(self, conn, message_data):
        """Sends a JSON message over the socket."""
        try:
            # Append a newline delimiter for message separation
            conn.sendall((json.dumps(message_data) + '\n').encode('utf-8'))
            return True
        except Exception:
            # Error implies client disconnection, handled by the main server loop
            return False

    def _get_next_available_task_id(self):
        """Pulls the next available task ID from any active group."""
        for group_id, task_list in self.task_groups.items():
            if task_list:
                return group_id, task_list.pop(0)
        return None, None
        
    def run(self):
        print(f"[{time.strftime('%H:%M:%S')}] [TASK BROKER] Starting up. Polling Celery Backend...")
        
        while self.running:
            addr, conn, name = self._get_idle_client_info()
            group_id, task_id = self._get_next_available_task_id()

            if conn and task_id:
                # 1. Fetch the packaged instructions from the Celery backend
                try:
                    task_result = AsyncResult(task_id, app=celery_app)
                    # We use .get() to pull the result (the payload dictionary) from Redis
                    payload_dict = task_result.get(timeout=3) 
                    
                    if not isinstance(payload_dict, dict) or payload_dict.get('type') != 'MD5_BRUTE_FORCE_CHUNK':
                        print(f"[{time.strftime('%H:%M:%S')}] [BROKER WARNING] Task {task_id[:8]}... returned invalid payload. Skipping.")
                        continue

                    # 2. Mark client as busy
                    self._set_client_status(addr, "BUSY") 

                    # 3. Send the task package
                    print(f"[{time.strftime('%H:%M:%S')}] [BROKER] Sending task {task_id[:8]}... to {name}.")
                    if self._send_message(conn, payload_dict):
                        pass # Success
                    else:
                        # Failed to send: re-queue the task ID for the next available worker
                        self.task_groups[group_id].insert(0, task_id) 
                        self._set_client_status(addr, "IDLE") 
                        print(f"[{time.strftime('%H:%M:%S')}] [BROKER ERROR] Failed to send task to {name}. Re-queued.")

                except Exception as e:
                    print(f"[{time.strftime('%H:%M:%S')}] [BROKER ERROR] Failed to fetch or process Celery task {task_id}: {e}. Re-queuing.")
                    self.task_groups[group_id].insert(0, task_id) 
                    self._set_client_status(addr, "IDLE") 
            
            time.sleep(self.polling_interval)

    def enqueue_group_tasks(self, group_id, num_tasks):
        """
        Fetches all task IDs belonging to a Celery group and adds them to the queue.
        """
        start_time = time.time()
        try:
            group_result = AsyncResult(group_id, app=celery_app)
            
            # Wait until the tasks are registered in the backend
            while not group_result.ready() and (time.time() - start_time) < 5:
                 time.sleep(0.1)
            
            # Extract the IDs of all individual tasks in the group
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