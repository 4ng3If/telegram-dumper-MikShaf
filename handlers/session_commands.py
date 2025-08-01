import os
import datetime
from utils.ui_utils import banner, generate_box, prompt, color, ok, info, success, warning, error
from utils.ui_utils import RED, GRN, YLW, BLU, MGA, CYN, RST, DIM
from utils.telegram_utils import parse_bot_token, is_bot_online, get_latest_messageid, get_bot_owner

def new_dumper(SESSION_DIR=None, API_ID=None, API_HASH=None):
    """Register a new bot session"""
    from utils.session_manager import SessionManager
    
    if SESSION_DIR is None:
        SESSION_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "telegram_data", "bot_sessions")
    
    session_mgr = SessionManager(SESSION_DIR)
    
    banner()
    print(generate_box([], -1, "Register New Bot", titleclr=GRN))
    bot_token = ""
    from_chat_id = ""

    try:
        while not bot_token:
            bot_token = input(prompt('Bot Token'))
        print("")
        while not from_chat_id:
            from_chat_id = input(prompt('Bot Chat ID'))
        print("")
    except KeyboardInterrupt:
        return

    
    bot_token = parse_bot_token(bot_token)
    bot_info = is_bot_online(bot_token)
    if not bot_info:
        print(f"{warning} Bot is offline. Try again.")
        input("\nPress ENTER to continue...")
        return

    bot_username = bot_info.get("username", "Unknown")
    bot_first_name = bot_info.get("first_name", "Unknown")

    
    session = session_mgr.load_single_session(bot_token, from_chat_id)

    
    if session:
        print(f"{info} Bot already registered: {bot_first_name} ({color(f'@{bot_username}', CYN)})")
        choice = input(prompt('Update existing session? (Y/n)')).lower()
        print("")
        
        if choice != 'n':
            session['last_updated_message_id'] = get_latest_messageid(bot_token, from_chat_id)
            session_mgr.save_sessions(bot_token, from_chat_id, session)
            print(f"{success} Session updated successfully!")
        else:
            print(f"{info} Session left unchanged.")
        
        input("\nPress ENTER to return to main menu...")
        return

    
    print(f"{info} Creating a new session...")
    session_name = input(prompt('Session Name (optional)'))
    print("")
    
    last_message_id = 1
    last_updated_message_id = get_latest_messageid(bot_token, from_chat_id)

    session = {
        "bot_token": bot_token,
        "from_chat_id": from_chat_id,
        "bot_owner": get_bot_owner(bot_token, from_chat_id),
        "last_message_id": last_message_id,
        "last_updated_message_id": last_updated_message_id,
        "username": bot_username,
        "first_name": bot_first_name,
        "session_name": session_name if session_name else f"{bot_first_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}",
        "is_done": False
    }
    session_mgr.save_sessions(bot_token, from_chat_id, session)
    
    print(f"{success} Bot {color(bot_first_name, GRN)} (@{color(bot_username, CYN)}) registered successfully!")
    print(f"{info} Use 'Saved Session' option from the main menu to work with this bot.")
    
    
    choice = input(prompt('Start dumping now? (Y/n)')).lower()
    print("")
    
    if choice == 'n':
        return
    else:
        from handlers.download_commands import download_all_messages
        download_all_messages(session, API_ID, API_HASH)

def show_sessions(session_manager=None, current_session=None, API_ID=None, API_HASH=None):
    """Displays available session files and allows selection."""
    from utils.session_manager import SessionManager
    
    if session_manager is None:
        session_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "telegram_data", "bot_sessions")
        session_manager = SessionManager(session_dir)
    
    banner()
    sessions = session_manager.load_sessions()
    
    if not sessions:
        print(f"{warning} No sessions found.")
        input("\nPress ENTER to continue...")
        return None

    
    session_list = list(sessions.values())
    
    
    checkpoint_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "checkpoints")
    checkpoint_files = []
    if os.path.exists(checkpoint_dir):
        checkpoint_files = [f for f in os.listdir(checkpoint_dir) if f.endswith("_progress.json")]
    
    
    for session in session_list:
        session_name = session.get("session_name", "Unnamed").replace(" ", "_")
        checkpoint_file = f"{session_name}_progress.json"
        
        if checkpoint_file in checkpoint_files:
            try:
                import json
                with open(os.path.join(checkpoint_dir, checkpoint_file), "r") as f:
                    checkpoint_data = json.load(f)
                
                
                session["has_checkpoint"] = True
                session["checkpoint_data"] = checkpoint_data
                
                
                if checkpoint_data.get("last_message_id", 0) > session.get("last_message_id", 0):
                    session["recoverable"] = True
                    session["recovery_point"] = checkpoint_data.get("last_message_id", 0)
            except Exception:
                
                pass
    
    
    active_sessions = [s for s in session_list if not s.get("is_done", False)]
    
    
    active_count = len(active_sessions)
    recoverable_count = sum(1 for s in active_sessions if s.get("recoverable", False))
    
    
    total_messages = sum(s.get("last_updated_message_id", 0) for s in active_sessions)
    downloaded_messages = sum(s.get("last_message_id", 0) for s in active_sessions)
    
    
    overall_percentage = 0
    if total_messages > 0:
        overall_percentage = min(100, round((downloaded_messages / total_messages) * 100))
    
    
    info_lines = [
        f"{ok} Active Sessions: {color(active_count, GRN)}",
        f"{ok} Download Status: {color(f'{overall_percentage}%', GRN if overall_percentage == 100 else YLW if overall_percentage > 50 else RED)} complete"
    ]
    print(generate_box(info_lines, -1, title='Sessions Info', titleclr=MGA, pos='left'))
    
    
    active_session_list = [s for s in session_list if not s.get("is_done", False)]
    
    
    active_session_list.sort(key=lambda s: s.get("session_name", "").lower())
    
    
    lists = []
    for idx, session_data in enumerate(active_session_list, start=1):
        session_name = session_data.get('session_name', 'Unnamed')
        
        
        if session_data.get("recoverable"):
            status = f"{color(' [INTERRUPTED]', MGA)}"
        else:
            status = ""
            
        
        progress = f"[{color(session_data['last_message_id'], YLW)}/{color(session_data['last_updated_message_id'], GRN)}]"
        
        
        total = session_data['last_updated_message_id']
        current = session_data['last_message_id']
        
        
        if session_data.get("recoverable") and session_data.get("recovery_point", 0) > current:
            original_current = current
            current = session_data.get("recovery_point")
            recovery_info = f" (Recoverable: {color(original_current, RED)} → {color(current, GRN)})"
        else:
            recovery_info = ""
            
        if total > 0:
            percentage = min(100, round((current / total) * 100))
            progress_color = GRN if percentage == 100 else YLW if percentage > 50 else RED
            progress += f" {color(f'{percentage}%', progress_color)}"
            
            
        
            
        lists.append(f"{color(idx, YLW, f'{DIM}[STR{DIM}]{RST}')} {color(session_name, MGA)} - {session_data['first_name']} ({color(f'@{session_data['username']}', CYN)}) {progress}{recovery_info}{status}")
    
    lists.append(f"{color('U', GRN, f'{DIM}[STR{DIM}]{RST}')} Update Active Sessions")
    lists.append(f"{color('C', RED, f'{DIM}[STR{DIM}]{RST}')} Clean Completed Sessions")
    lists.append(f"{color('ENTER', CYN, f'{DIM}[STR{DIM}]{RST}')} Back/Cancel")
    print(generate_box(lists, -1, title='List Session', pos='left'))
    
    choice = input(prompt('Select Session'))
    print("")
    
    if choice.isdigit():
        choice = int(choice) - 1
        if 0 <= choice < len(active_session_list):
            selected_session = active_session_list[choice]
            session_name = selected_session.get('session_name', 'Unnamed')
            
            
            if selected_session.get("recoverable"):
                checkpoint_data = selected_session.get("checkpoint_data", {})
                original_message_id = selected_session["last_message_id"]
                recovery_point = selected_session["recovery_point"]
                
                print(f"{info} Found interrupted session that can be recovered.")
                print(f"{info} Current progress: {color(original_message_id, YLW)}")
                print(f"{info} Recoverable progress: {color(recovery_point, GRN)} (+{recovery_point - original_message_id} messages)")
                
                
                recover_choice = input(prompt(f"Recover from checkpoint? (Y/n)")).lower()
                print("")
                
                if recover_choice != "n":
                    
                    checkpoint_file = os.path.join(
                        os.path.dirname(os.path.dirname(__file__)), 
                        "checkpoints",
                        f"{session_name.replace(' ', '_')}_progress.json"
                    )
                    
                    print(f"{info} Recovering session from checkpoint...")
                    
                    
                    selected_session["last_message_id"] = recovery_point
                    
                    
                    try:
                        if os.path.exists(checkpoint_file):
                            os.remove(checkpoint_file)
                            print(f"{success} Checkpoint recovered and cleaned up.")
                    except Exception as e:
                        print(f"{warning} Couldn't remove checkpoint file: {e}")
            
            
            selected_session['is_done'] = False
            selected_session['last_updated_message_id'] = get_latest_messageid(selected_session['bot_token'], selected_session['from_chat_id'])
            
            
            session_manager.save_sessions(selected_session['bot_token'], selected_session['from_chat_id'], selected_session)
            
            
            print(f"{success} Session activated: {color(selected_session.get('session_name', 'Unnamed'), MGA)} (@{color(selected_session.get('username', 'Unknown'), CYN)})")
            
            return selected_session
        else:
            print(f"{warning} Invalid choice.")
            input("\nPress ENTER to continue...")
            return None
            
    if str(choice).lower() == "u":
        
        for session in active_session_list:
            session["last_updated_message_id"] = get_latest_messageid(session['bot_token'], session['from_chat_id'])
            print(f"\n{ok} Session for {session.get('session_name', 'Unnamed')} - {session['first_name']} ({color(f'@{session['username']}', CYN)}) updated.")
            
            session_manager.save_sessions(session['bot_token'], session['from_chat_id'], session)
        
        input("\nActive Sessions Updated! Press ENTER to continue...")
        return show_sessions(session_manager, current_session, API_ID, API_HASH)
    
    if str(choice).lower() == "c":
        
        completed_sessions = [s for s in session_list if s.get("is_done", False)]
        
        if not completed_sessions:
            print(f"{info} No completed sessions to clean.")
            input("\nPress ENTER to continue...")
            return show_sessions(session_manager, current_session, API_ID, API_HASH)
        
        
        print(f"{warning} About to remove {color(len(completed_sessions), RED)} completed sessions.")
        confirm = input(prompt(f"Are you sure? (y/N)")).lower()
        
        if confirm == "y":
            cleaned_count = 0
            for session in completed_sessions:
                try:
                    
                    bot_token = session['bot_token']
                    chat_id = session['from_chat_id']
                    session_name = session.get('session_name', 'Unnamed')
                    
                    
                    file_path = session_manager.get_session_filepath(bot_token, chat_id, session_name)
                    
                    
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        cleaned_count += 1
                        print(f"{ok} Removed session: {color(session_name, MGA)} (@{color(session.get('username', 'Unknown'), CYN)})")
                except Exception as e:
                    print(f"{error} Failed to remove session {session.get('session_name', 'Unnamed')}: {e}")
            
            print(f"\n{success} Cleaned {color(cleaned_count, GRN)} completed sessions.")
            input("\nPress ENTER to continue...")
        else:
            print(f"{info} Operation cancelled.")
            input("\nPress ENTER to continue...")
        
        return show_sessions(session_manager, current_session, API_ID, API_HASH)
    
    return None
