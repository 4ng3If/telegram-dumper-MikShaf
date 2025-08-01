import os
import threading
import datetime
import time
from utils.ui_utils import banner, generate_box, prompt, color, ok, info, success, warning, error
from utils.ui_utils import RED, GRN, YLW, BLU, MGA, CYN, RST, DIM
from utils.telegram_utils import get_latest_messageid
from utils.background_worker import enqueue_background_job, is_download_in_progress, get_current_download_session


auto_update_threads = {}

def auto_update_messages(session_data, interval=1200, daemon=True):
    from utils.session_manager import SessionManager
    
    session_mgr = SessionManager(os.path.join(os.path.dirname(os.path.dirname(__file__)), "session"))
    
    bot_token = session_data.get('bot_token')
    chat_id = session_data.get('from_chat_id')
    session_name = session_data.get('session_name', 'Unnamed')
    
    
    last_check_time = time.time()
    last_message_id = session_data.get('last_message_id', 1)
    
    thread_id = f"{bot_token}:{chat_id}"
    
    print(f"{info} Starting auto-update for {color(session_name, MGA)} ({color('@'+session_data.get('username', 'Unknown'), CYN)})")
    print(f"{info} Checking every {interval//60} minutes for new messages")
    
    while True:
        try:
            current_time = time.time()
            
            
            if current_time - last_check_time >= interval:
                
                latest_message_id = get_latest_messageid(bot_token, chat_id)
                
                if latest_message_id is None:
                    print(f"{error} Couldn't get latest message ID for {color(session_name, MGA)}")
                    
                    time.sleep(60)
                    continue
                
                
                if latest_message_id > last_message_id:
                    num_new_messages = latest_message_id - last_message_id
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    
                    log_dir = "logs"
                    if not os.path.exists(log_dir):
                        os.makedirs(log_dir)
                    
                    log_file = os.path.join(log_dir, "auto_update.log")
                    with open(log_file, "a") as f:
                        f.write(f"[{timestamp}] Found {num_new_messages} new messages for {session_name}\n")
                        f.write(f"[{timestamp}] Queueing download for messages {last_message_id+1} to {latest_message_id}\n")
                    
                    
                    enqueue_background_job(
                        bot_token=bot_token, 
                        chat_id=chat_id, 
                        num_messages=num_new_messages, 
                        message_id=latest_message_id,
                        session_name=session_name
                    )
                    
                    
                    session_data['last_message_id'] = latest_message_id
                    session_mgr.save_sessions(bot_token, chat_id, session_data)
                    
                    
                    last_message_id = latest_message_id
                else:
                    
                    pass
                
                
                last_check_time = current_time
            
            
            time.sleep(60)
            
        except KeyboardInterrupt:
            
            break
        except Exception as e:
            
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            log_file = os.path.join(log_dir, "auto_update_errors.log")
            with open(log_file, "a") as f:
                f.write(f"[{timestamp}] Error in auto-update for {session_name}: {str(e)}\n")
                
            
            time.sleep(60)

def start_auto_update(current_session=None):
    """Start automatic checking for new messages every 20 minutes"""
    global auto_update_threads
    from utils.session_manager import SessionManager
    
    session_mgr = SessionManager(os.path.join(os.path.dirname(os.path.dirname(__file__)), "session"))
    
    banner()
    print(generate_box([], -1, "Auto-Update Messages", titleclr=GRN))
    
    if not current_session:
        
        sessions = session_mgr.load_sessions()
        
        if not sessions:
            print(f"{error} No sessions found. Please create a session first.")
            input("\nPress ENTER to continue...")
            return
            
        
        session_list = list(sessions.values())
        
        
        session_list.sort(key=lambda s: (s.get("is_done", False), s.get("session_name", "").lower()))
        
        print(f"{info} Select a session to auto-update:")
        
        lists = []
        for idx, session_data in enumerate(session_list, start=1):
            session_name = session_data.get('session_name', 'Unnamed')
            thread_id = f"{session_data.get('bot_token')}:{session_data.get('from_chat_id')}"
            status = "Running" if thread_id in auto_update_threads and auto_update_threads[thread_id].is_alive() else "Stopped"
            status_color = GRN if status == "Running" else RED
            
            lists.append(f"{color(idx, YLW, f'{DIM}[STR{DIM}]{RST}')} {color(session_name, MGA)} - {session_data['first_name']} ({color('@'+session_data.get('username', 'Unknown'), CYN)}) [{color(status, status_color)}]")
        
        lists.append(f"{color('A', GRN, f'{DIM}[STR{DIM}]{RST}')} Start All Sessions")
        lists.append(f"{color('ENTER', CYN, f'{DIM}[STR{DIM}]{RST}')} Back/Cancel")
        print(generate_box(lists, -1, title='Select Session', pos='left'))
        
        choice = input(prompt('Select Session'))
        print("")
        
        if choice.lower() == 'a':
            
            for session in session_list:
                thread_id = f"{session.get('bot_token')}:{session.get('from_chat_id')}"
                
                
                if thread_id in auto_update_threads and auto_update_threads[thread_id].is_alive():
                    print(f"{warning} Auto-update already running for {color(session.get('session_name', 'Unnamed'), MGA)}")
                    continue
                    
                
                update_thread = threading.Thread(
                    target=auto_update_messages,
                    args=(session,),
                    daemon=True  
                )
                update_thread.start()
                
                
                auto_update_threads[thread_id] = update_thread
            
            print(f"{success} Started auto-update for all sessions!")
            input("\nPress ENTER to continue...")
            return
            
        elif choice.isdigit():
            choice = int(choice) - 1
            if 0 <= choice < len(session_list):
                selected_session = session_list[choice]
                thread_id = f"{selected_session.get('bot_token')}:{selected_session.get('from_chat_id')}"
                
                
                if thread_id in auto_update_threads and auto_update_threads[thread_id].is_alive():
                    print(f"{warning} Auto-update already running for {color(selected_session.get('session_name', 'Unnamed'), MGA)}")
                    input("\nPress ENTER to continue...")
                    return
                
                
                update_thread = threading.Thread(
                    target=auto_update_messages,
                    args=(selected_session,),
                    daemon=True  
                )
                update_thread.start()
                
                
                auto_update_threads[thread_id] = update_thread
                
                print(f"{success} Started auto-update for {color(selected_session.get('session_name', 'Unnamed'), MGA)}")
                input("\nPress ENTER to continue...")
                return
            else:
                print(f"{error} Invalid choice.")
                input("\nPress ENTER to continue...")
                return
    else:
        
        thread_id = f"{current_session.get('bot_token')}:{current_session.get('from_chat_id')}"
        
        
        if thread_id in auto_update_threads and auto_update_threads[thread_id].is_alive():
            print(f"{warning} Auto-update already running for {color(current_session.get('session_name', 'Unnamed'), MGA)}")
            input("\nPress ENTER to continue...")
            return
        
        
        update_thread = threading.Thread(
            target=auto_update_messages,
            args=(current_session,),
            daemon=True  
        )
        update_thread.start()
        
        
        auto_update_threads[thread_id] = update_thread
        
        print(f"{success} Started auto-update for {color(current_session.get('session_name', 'Unnamed'), MGA)}")
        input("\nPress ENTER to continue...")

def stop_auto_update():
    """Stop automatic checking for new messages"""
    global auto_update_threads
    from utils.session_manager import SessionManager
    
    session_mgr = SessionManager(os.path.join(os.path.dirname(os.path.dirname(__file__)), "session"))
    
    banner()
    print(generate_box([], -1, "Stop Auto-Update", titleclr=RED))
    
    
    if is_download_in_progress() and get_current_download_session():
        current_download_session = get_current_download_session()
        session_name = current_download_session.get('session_name', 'Unknown')
        print(f"{warning} There's an active download in progress for {color(session_name, MGA)}")
        print(f"{info} The download will continue until completion")
        
    if not auto_update_threads:
        print(f"{info} No auto-update processes running.")
        input("\nPress ENTER to continue...")
        return
    
    
    running_threads = {k: v for k, v in auto_update_threads.items() if v.is_alive()}
    
    if not running_threads:
        print(f"{info} No auto-update processes running.")
        input("\nPress ENTER to continue...")
        return
    
    
    running_sessions = []
    for thread_id, thread in running_threads.items():
        parts = thread_id.split(':', 1)
        if len(parts) != 2:
            print(f"{warning} Skipping malformed thread_id: {thread_id}")
            continue
            
        bot_token, chat_id = parts
        session = session_mgr.load_single_session(bot_token, chat_id)
        if session:
            running_sessions.append((thread_id, session))
    
    
    lists = []
    for idx, (thread_id, session) in enumerate(running_sessions, start=1):
        session_name = session.get('session_name', 'Unnamed')
        lists.append(f"{color(idx, YLW, f'{DIM}[STR{DIM}]{RST}')} {color(session_name, MGA)} - {session['first_name']} ({color('@'+session.get('username', 'Unknown'), CYN)})")
    
    lists.append(f"{color('A', RED, f'{DIM}[STR{DIM}]{RST}')} Stop All")
    lists.append(f"{color('ENTER', CYN, f'{DIM}[STR{DIM}]{RST}')} Back/Cancel")
    print(generate_box(lists, -1, title='Select Session to Stop', pos='left'))
    
    choice = input(prompt('Select Session'))
    print("")
    
    if choice.lower() == 'a':
        
        auto_update_threads.clear()
        print(f"{success} Stopped all auto-update processes!")
        print(f"{info} Note: Processes will terminate on next check cycle")
        input("\nPress ENTER to continue...")
        return
    
    elif choice.isdigit():
        choice = int(choice) - 1
        if 0 <= choice < len(running_sessions):
            thread_id, selected_session = running_sessions[choice]
            
            
            if thread_id in auto_update_threads:
                del auto_update_threads[thread_id]
                
                print(f"{success} Stopped auto-update for {color(selected_session.get('session_name', 'Unnamed'), MGA)}")
                print(f"{info} Note: Process will terminate on next check cycle")
            else:
                print(f"{warning} Auto-update process not found.")
                
            input("\nPress ENTER to continue...")
            return
        else:
            print(f"{error} Invalid choice.")
            input("\nPress ENTER to continue...")
            return

def show_auto_update_status(background_worker_thread=None):
    """Show the status of all auto-update threads"""
    global auto_update_threads
    from utils.session_manager import SessionManager
    
    session_mgr = SessionManager(os.path.join(os.path.dirname(os.path.dirname(__file__)), "session"))
    
    banner()
    print(generate_box([], -1, "Auto-Update Status", titleclr=BLU))
    
    
    if background_worker_thread and background_worker_thread.is_alive():
        worker_status = f"Background worker: {color('RUNNING', GRN)}"
    else:
        worker_status = f"Background worker: {color('STOPPED', RED)}"
    
    
    if is_download_in_progress() and get_current_download_session():
        current_download_session = get_current_download_session()
        session_name = current_download_session.get('session_name', 'Unknown')
        start_time = current_download_session.get('start_time', 'Unknown')
        num_msgs = current_download_session.get('num_messages', 'Unknown')
        active_download = f"ACTIVE DOWNLOAD: {color(session_name, MGA)} ({num_msgs} msgs) - Started: {color(start_time, YLW)}"
    else:
        active_download = f"No active downloads"
    
    
    print(f"{ok} {worker_status}")
    print(f"{ok} {active_download}")
    print("")
        
    
    if not auto_update_threads:
        print(f"{info} No auto-update processes are monitoring channels.")
    else:
        lists = []
        count = 0
        
        for thread_id, thread in auto_update_threads.items():
            
            if not thread.is_alive():
                continue
                
            count += 1
            
            
            parts = thread_id.split(':', 1)
            if len(parts) != 2:
                lists.append(f"{color('Unknown', RED)} - Malformed thread ID: {thread_id}")
                continue
                
            
            bot_token, chat_id = parts
            session = session_mgr.load_single_session(bot_token, chat_id)
            
            if not session:
                lists.append(f"{color('Unknown', RED)} - Bot token: {bot_token[:10]}... Chat: {chat_id}")
                continue
                
            
            session_name = session.get('session_name', 'Unnamed')
            username = session.get('username', 'Unknown')
            first_name = session.get('first_name', 'Unknown')
            
            lists.append(f"{color(session_name, MGA)} - {first_name} ({color('@'+username, CYN)}) [{color('MONITORING', GRN)}]")
        
        if count == 0:
            print(f"{info} No active auto-update processes are monitoring channels.")
        else:
            print(f"{info} {color(count, GRN)} active auto-update processes:")
            print(generate_box(lists, -1, title='Monitored Channels', pos='left'))
    
    input("\nPress ENTER to continue...")
