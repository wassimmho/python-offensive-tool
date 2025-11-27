# socket_tasks.py (Defines the task that packages work instructions)

from celery import Celery
from Mohamed.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

# Setup Celery Application 
app = Celery('socket_tasks',
             broker=CELERY_BROKER_URL,
             backend=CELERY_RESULT_BACKEND)

@app.task(bind=True)
def package_socket_task(self, target_encryption, length, start_prefix=None):
    """
    Celery task: Creates a structured payload for the Socket Server to distribute.
    """
    
    # Calculate the remaining length for the client to brute-force
    prefix_len = len(start_prefix) if start_prefix else 0
    remaining_length = length - prefix_len
    
    # This dictionary is what the Socket Broker will fetch and send to a client
    payload = {
        "task_id": self.request.id, 
        "type": "MD5_BRUTE_FORCE_CHUNK",
        "target_hash": target_encryption,
        "prefix": start_prefix or "",
        "suffix_length": remaining_length,
        # Client needs to know the character set too, so we send it along
        "charset": list(set(__import__('config').CHARACTER_SET)) 
    }
    
    return payload

@app.task
def handle_completion_callback(results):
    """
    The final callback for the Celery Chord.
    """
    print("\n" + "=" * 70)
    print("✅ CELERY DISPATCH PHASE COMPLETE.")
    print(f"Total task packages created and available for socket distribution: {len(results)}")
    print("The TaskBroker thread will now pull these and send them to idle Socket Clients...")
    print("=" * 70)