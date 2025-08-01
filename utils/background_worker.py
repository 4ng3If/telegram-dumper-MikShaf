import queue
import threading
import datetime
import os
import time
import json
import multiprocessing
from utils.ui_utils import color, info, error, warning, CYN, MGA


background_job_queue = queue.Queue()
worker_running = False
background_worker_thread = None
download_in_progress = False
current_download_session = None

def enqueue_background_job(bot_token, chat_id, num_messages, message_id, session_name):
    """Add a job to the background processing queue"""
    global background_job_queue, worker_running, background_worker_thread
    
    
    job = {
        "bot_token": bot_token,
        "chat_id": chat_id,
        "num_messages": num_messages,
        "message_id": message_id,
        "session_name": session_name,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    background_job_queue.put(job)
    
    
    if not worker_running or (background_worker_thread is not None and not background_worker_thread.is_alive()):
        start_background_worker()
        
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{color(timestamp, CYN)}] {info} Queued download job for {color(session_name, MGA)} ({num_messages} messages)")


def start_background_worker():
    """Start a background thread to process jobs from the queue"""
    global worker_running, background_worker_thread
    
    if worker_running:
        return  
        
    worker_running = True
    background_worker_thread = threading.Thread(target=background_worker_loop, daemon=True)
    background_worker_thread.start()
    
def stop_background_worker():
    """Stop the background worker thread gracefully"""
    global worker_running, background_worker_thread
    
    if not worker_running:
        return  
    
    
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, "background_jobs.log")
    timestamp_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp_now}] Stopping background message processor\n")
    
    worker_running = False
    
    
    if background_worker_thread and background_worker_thread.is_alive():
        background_worker_thread.join(timeout=5)
    
    
    timestamp_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp_now}] Background message processor stopped\n")
    
    
def background_worker_loop():
    """Main loop for processing background jobs"""
    global background_job_queue, worker_running, download_in_progress, current_download_session
    
    
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, "background_jobs.log")
    timestamp_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp_now}] Starting background message processor\n")
    
    try:
        while worker_running:
            try:
                
                job = background_job_queue.get(timeout=5)
                
                
                bot_token = job["bot_token"]
                chat_id = job["chat_id"]
                num_messages = job["num_messages"]
                message_id = job["message_id"]
                session_name = job["session_name"]
                timestamp = job["timestamp"]
                
                try:
                    
                    timestamp_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_dir = "logs"
                    if not os.path.exists(log_dir):
                        os.makedirs(log_dir)
                    
                    
                    log_file = os.path.join(log_dir, "background_jobs.log")
                    
                    
                    download_in_progress = True
                    current_download_session = {
                        "bot_token": bot_token,
                        "chat_id": chat_id,
                        "session_name": session_name,
                        "start_time": timestamp_now,
                        "num_messages": num_messages
                    }
                    
                    with open(log_file, "a") as f:
                        f.write(f"[{timestamp_now}] Processing download for {session_name}\n")
                    
                    
                    mp_context = multiprocessing.get_context('spawn')
                    process = mp_context.Process(
                        target=run_process_messages,
                        args=(bot_token, chat_id, num_messages, message_id)
                    )
                    process.start()
                    process.join()  
                    
                    
                    download_in_progress = False
                    current_download_session = None
                    
                    
                    background_job_queue.task_done()
                    
                    
                    timestamp_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with open(log_file, "a") as f:
                        f.write(f"[{timestamp_now}] Successfully downloaded messages for {session_name}\n")
                    
                except Exception as e:
                    
                    timestamp_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_dir = "logs"
                    if not os.path.exists(log_dir):
                        os.makedirs(log_dir)
                    
                    log_file = os.path.join(log_dir, "background_errors.log")
                    with open(log_file, "a") as f:
                        f.write(f"[{timestamp_now}] Failed to process download for {session_name}: {str(e)}\n")
                    
                    background_job_queue.task_done()
                    
            except queue.Empty:
                
                pass
                
            except Exception as e:
                
                timestamp_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_dir = "logs"
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                
                log_file = os.path.join(log_dir, "background_errors.log")
                with open(log_file, "a") as f:
                    f.write(f"[{timestamp_now}] Error in background worker: {str(e)}\n")
                
            
            time.sleep(0.1)
            
    finally:
        worker_running = False
        print(f"{info} Background message processor stopped")


def run_process_messages(bot_token, chat_id, num_messages, message_id):
    """Run process_messages in a way that properly handles the event loop"""
    
    from handlers.mikshaf_viewer import process_messages
    import os
    
    
    from dotenv import load_dotenv
    load_dotenv()
    API_ID = os.getenv("API_ID")
    API_HASH = os.getenv("API_HASH")
    
    try:
        
        process_messages(bot_token, chat_id, num_messages, message_id, API_ID, API_HASH)
    except Exception as e:
        print(f"{error} Error in process_messages: {str(e)}")

def is_download_in_progress():
    global download_in_progress
    return download_in_progress

def get_current_download_session():
    global current_download_session
    return current_download_session
