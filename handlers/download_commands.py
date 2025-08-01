import os
import sys
import time
import datetime
from utils.ui_utils import banner, generate_box, prompt, color, ok, info, success, warning, error
from utils.ui_utils import RED, GRN, YLW, BLU, MGA, CYN, RST, DIM
from utils.telegram_utils import parse_bot_token, is_bot_online, get_latest_messageid
from utils.background_worker import enqueue_background_job

def download_all_messages(use_session=None, API_ID=None, API_HASH=None):
    """Download all messages from a chat"""
    from utils.session_manager import SessionManager
    
    session_mgr = SessionManager(os.path.join(os.path.dirname(os.path.dirname(__file__)), "session"))
    
    banner()
    print(generate_box([], -1, "Download All Messages", titleclr=GRN))
    
    bot_token = ""
    chat_id = ""
    
    
    current_session = None
    if 'current_session' in globals():
        current_session = globals()['current_session']
    
    if use_session is None and current_session:
        use_current = input(prompt(f'Use current session ({color(current_session.get("session_name", "Unnamed"), MGA)})? (Y/n)')).lower() != 'n'
        print("")
        
        if use_current:
            use_session = current_session
            bot_token = current_session['bot_token']
            chat_id = current_session['from_chat_id']
            print(f"{info} Using current session: {color(current_session.get('session_name', 'Unnamed'), MGA)} (@{color(current_session.get('username', 'Unknown'), CYN)})")
    
    if use_session is None:
        sessions = session_mgr.load_sessions()
        
        if sessions:
            use_existing = input(prompt('Use existing session? (Y/n)')).lower() != 'n'
            print("")
            
            if use_existing:
                
                session_list = list(sessions.values())
                active_sessions = [s for s in session_list if not s.get("is_done", False)]
                completed_sessions = [s for s in session_list if s.get("is_done", True)]
                
                
                active_sessions.sort(key=lambda s: s.get("session_name", "").lower())
                completed_sessions.sort(key=lambda s: s.get("session_name", "").lower())
                
                
                all_sessions_list = active_sessions + completed_sessions
                
                lists = []
                for idx, session_data in enumerate(all_sessions_list, start=1):
                    session_name = session_data.get('session_name', 'Unnamed')
                    status = "" if not session_data.get("is_done") else f"{color(' [COMPLETED]', YLW)}"
                    
                    lists.append(f"{color(idx, YLW, f'{DIM}[STR{DIM}]{RST}')} {color(session_name, MGA)} - {session_data['first_name']} ({color(f'@{session_data['username']}', CYN)}){status}")
                
                lists.append(f"{color('N', GRN, f'{DIM}[STR{DIM}]{RST}')} New Session")
                print(generate_box(lists, -1, title='Select Session for Download', pos='left'))
                
                choice = input(prompt('Select Session')).strip()
                print("")
                
                if choice.lower() == 'n':
                    
                    pass
                elif choice.isdigit() and 0 < int(choice) <= len(all_sessions_list):
                    
                    selected_session = all_sessions_list[int(choice)-1]
                    bot_token = selected_session['bot_token']
                    chat_id = selected_session['from_chat_id']
                    print(f"{info} Using session: {color(selected_session.get('session_name', 'Unnamed'), MGA)}")
                    print(f"{info} Bot: {color(f'@{selected_session['username']}', CYN)}")
                    print(f"{info} Chat ID: {color(chat_id, GRN)}")
                else:
                    print(f"{error} Invalid selection.")
                    input("\nPress ENTER to continue...")
                    return
    else:
        
        bot_token = use_session['bot_token']
        chat_id = use_session['from_chat_id']
        print(f"{info} Using session: {color(use_session.get('session_name', 'Unnamed'), MGA)}")
    
    
    try:
        if not bot_token:
            while not bot_token:
                bot_token = input(prompt('Bot Token'))
            print("")
            
        if not chat_id:
            while not chat_id:
                chat_id = input(prompt('Chat ID'))
            print("")
        
        
        print(f"{info} Fetching latest message ID...")
        message_id = get_latest_messageid(bot_token, chat_id)
        
        if message_id is None:
            print(f"{warning} Could not determine last message ID.")
            message_id = input(prompt('Enter Last Message ID manually'))
            if not message_id.isdigit():
                print(f"{error} Invalid message ID.")
                input("\nPress ENTER to continue...")
                return
            message_id = int(message_id)
        
        print(f"\n{info} TOTAL NUMBER OF MESSAGES: ~{color(message_id, GRN)}")
        
        
        num_messages_input = input(prompt('Press ENTER to retrieve all messages or enter a number (Downloading from Newest to Oldest)'))
        if num_messages_input == "":
            num_messages = message_id
        else:
            try:
                num_messages = int(num_messages_input)
            except ValueError:
                print(f"{error} Invalid number.")
                input("\nPress ENTER to continue...")
                return
        
        
        question = input(prompt('Would you like to start from a specific message_id? (y/n)'))
        if question.lower() == 'y':
            try:
                message_id = int(input(prompt(f'Enter the message_id offset to start from')))
            except ValueError:
                print(f"{error} Invalid message ID.")
                input("\nPress ENTER to continue...")
                return
        
    except KeyboardInterrupt:
        return
    
    bot_token = parse_bot_token(bot_token)
    
    
    bot_info = is_bot_online(bot_token)
    if not bot_info:
        print(f"{error} Bot is offline or token is invalid. Try again.")
        input("\nPress ENTER to continue...")
        return
    
    
    if use_session is None:
        save_as_session = input(prompt('Save as a session for future use? (Y/n)')).lower() != 'n'
        print("")
        
        if save_as_session:
            session_name = input(prompt('Session name (optional)'))
            print("")
            
            
            bot_info = is_bot_online(bot_token)
            bot_username = bot_info.get('username', '')
            bot_first_name = bot_info.get('first_name', '')
            
            
            session_data = {
                'session_name': session_name or f"{bot_first_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}",
                'bot_token': bot_token,
                'from_chat_id': chat_id,
                'username': bot_username,
                'first_name': bot_first_name,
                'last_message_id': 1,
                'last_updated_message_id': message_id,
                'is_done': False,
                'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            
            session_mgr.save_sessions(bot_token, chat_id, session_data)
            print(f"{ok} Session saved as: {color(session_data['session_name'], MGA)}")
            print("")
    
    print(f"{info} Downloading {color(num_messages, GRN)} messages from chat ID: {color(chat_id, YLW)} starting from message {color(message_id, MGA)}...")
    
    
    queue_download = input(prompt('Queue as background job? (y/N)')).lower() == 'y'
    print("")
    
    if queue_download:
        session_name = use_session.get('session_name', 'Unknown') if use_session else f"New_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}"
        enqueue_background_job(bot_token, chat_id, num_messages, message_id, session_name)
        print(f"{success} Download queued successfully!")
        input("\nPress ENTER to continue...")
        return
    
    try:
        
        start_time = time.time()
        
        
        from handlers.mikshaf_viewer import process_messages
        print(f"{info} Using bot token for authentication: {color(bot_token, YLW)}")
        process_messages(bot_token, chat_id, num_messages, message_id, API_ID, API_HASH)
        
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"\n{success} Download operation completed!")
        print(f"{ok} Time elapsed: {color(f'{elapsed_time:.1f} seconds', YLW)}")
        print(f"{ok} Messages downloaded to: {color('Downloads/' + chat_id, GRN)}")
        
        
        if use_session:
            use_session['last_message_id'] = message_id
            use_session['is_done'] = True
            session_mgr.save_sessions(bot_token, chat_id, use_session)
            print(f"{ok} Session updated with download progress.")
        
    except Exception as e:
        print(f"\n{error} An error occurred: {e}")
        print(f"{info} Make sure you have the API_ID and API_HASH environment variables set correctly.")
    except KeyboardInterrupt:
        print(f"\n{warning} Operation interrupted.")
        print(f"{info} Some messages may have been downloaded before interruption.")
        print(f"{info} Check the Downloads folder for partial results.")
    
    input("\nPress ENTER to continue...")
