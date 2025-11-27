# task_dispatcher.py (Runs the master interface and scheduling)

import sqlite3
import hashlib
import time
import itertools
import math
import sys
from celery import chord, group
from Mohamed.socket_tasks import package_socket_task, handle_completion_callback
from Mohamed.config import MAX_PATTERN_LENGTH, CHARACTER_SET, CELERY_BROKER_URL

# --- Database Management (Uses MD5, as per original user code) ---
DB_FILE = "crypto_research.db"

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

    def get_entry_encryption(self, entry_id):
        self.cur.execute("SELECT encrypted_pattern FROM research_entries WHERE entry_id=?", (entry_id,))
        row = self.cur.fetchone()
        return row[0] if row else None
    
    def get_all_entries(self):
        self.cur.execute("SELECT entry_id FROM research_entries")
        return [entry[0] for entry in self.cur.fetchall()]

# --- Main Dispatcher Logic ---

class DistributedPatternDiscoveryEngine:
    """Manages task distribution based on worker count."""
    
    def __init__(self):
        self.db = ResearchDBManager()
        self.char_set_size = len(CHARACTER_SET)
        print(f"[{time.strftime('%H:%M:%S')}] Dispatcher initialized. Broker: {CELERY_BROKER_URL}")

    def get_task_splitting_prefixes(self, length, num_workers):
        """
        SMART ALGORITHM: Calculates the best prefix length to split the work 
        to ensure all 'num_workers' are kept busy.
        """
        
        # If length is small or the total possibilities are less than workers, no split needed
        if length <= 2 or self.char_set_size ** length <= num_workers:
            return [None]

        # Calculate the required prefix length (p) to create at least 'num_workers' chunks
        required_prefix_len = math.ceil(math.log(num_workers) / math.log(self.char_set_size))
        prefix_len = min(int(required_prefix_len), length)

        if prefix_len == 0:
            return [None]

        # Generate all prefixes
        prefixes = ["".join(p) for p in itertools.product(CHARACTER_SET, repeat=prefix_len)]
        return prefixes


    def discover_original_pattern_distributed(self, entry_id, num_workers):
        """
        Splits the search space and dispatches task PACKAGES to Celery.
        """
        target_encryption = self.db.get_entry_encryption(entry_id)
        if target_encryption is None:
            print("Research entry not found in database.")
            return

        print(f"\n🔍 DISTRIBUTING PATTERN DISCOVERY for: {entry_id}")
        print(f"Target encryption: {target_encryption}")

        task_signatures = []
        total_tasks_submitted = 0
        start_time = time.time()

        for length in range(1, MAX_PATTERN_LENGTH + 1):
            prefixes = self.get_task_splitting_prefixes(length, num_workers)
            
            print(f"  - Length {length}: Smartly splitting into {len(prefixes)} task(s).")
            
            for prefix in prefixes:
                task_signatures.append(
                    package_socket_task.s(target_encryption, length, prefix)
                )
            total_tasks_submitted += len(prefixes)
        
        if not task_signatures:
             print("No tasks generated. Check MAX_PATTERN_LENGTH and CHARACTER_SET settings.")
             return
             
        print(f"\nSubmitting a total of **{total_tasks_submitted}** task PACKAGES to the distributed queue...")
        
        # Chord submits the group of header tasks, and when they are all complete (packaged), 
        # it calls the final callback.
        job = chord(
            group(task_signatures), 
            callback=handle_completion_callback.s()
        )
        
        job_result = job.apply_async() 
        print(f"Job submitted. Celery Job ID: {job_result.id}")
        
        # We return the Chord's parent group ID which contains all individual task IDs
        return job_result.parent.id, total_tasks_submitted


def main(broker_ref=None):
    """
    Main function for the Dispatcher. Accepts a reference to the TaskBroker 
    if running in a combined environment (main_server.py).
    """
    analyzer = DistributedPatternDiscoveryEngine()

    while True:
        print("\n🔬 SMART DISTRIBUTED HASH DISCOVERY SYSTEM (Dispatcher)")
        print("=" * 60)
        print("1. Add research entry (Pattern -> MD5)")
        print("2. View research entries")
        print("3. **Automatic** Distributed Pattern Search (Max Len 6)")
        print("4. Exit system")
        print("=" * 60)

        choice = input("Select operation: ")

        if choice == "1":
            entry_id = input("Research entry ID: ")
            pattern_data = input("Pattern data to encrypt: ")
            analyzer.db.add_research_entry(entry_id, pattern_data)
            print("Research entry added successfully.")

        elif choice == "2":
            print("Research entries in database:")
            entries = analyzer.db.get_all_entries()
            if entries:
                for entry in entries:
                    print(f" • {entry}")
            else:
                print("No research entries found.")

        elif choice == "3":
            try:
                num_workers = int(input("Enter the **TOTAL** number of available PCs/Workers: "))
                if num_workers <= 0:
                    raise ValueError
                entry_id = input("Research entry ID to analyze: ")
                
                # Get the Chord's parent group ID (containing all task IDs)
                group_id, num_tasks = analyzer.discover_original_pattern_distributed(entry_id, num_workers)
                
                # If we are running in the combined server, enqueue the task IDs
                if broker_ref:
                    print(f"[{time.strftime('%H:%M:%S')}] Notifying TaskBroker of {num_tasks} new tasks...")
                    broker_ref.enqueue_group_tasks(group_id, num_tasks)


            except ValueError:
                print("Invalid number of workers. Please enter a positive integer.")

        elif choice == "4":
            print("Closing dispatcher.")
            break

        else:
            print("Invalid selection. Please choose 1-4.")

if __name__ == "__main__":
    print("WARNING: Running standalone. Use 'python main_server.py' to run with the TaskBroker.")
    main()