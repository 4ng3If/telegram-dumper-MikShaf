

import os
import sys
from utils.ui_utils import banner, generate_box, prompt, color, ok, info, success, warning, error
from utils.ui_utils import RED, GRN, YLW, BLU, MGA, CYN, RST, DIM
from utils.telegram_utils import is_telethon_authenticated
from utils.background_worker import start_background_worker, stop_background_worker, background_worker_thread

def main_menu():    
    from handlers.auth_commands import init
    TO_CHAT_ID, API_ID, API_HASH = init()
    
    
    start_background_worker()
    
    
    current_session = None
    
    try:
        while True:
            banner()
            
            
            session_info = ""
            if current_session:
                bot_name = current_session.get('first_name', 'Unknown')
                bot_username = current_session.get('username', 'Unknown')
                session_name = current_session.get('session_name', 'Unnamed')
                chat_id = current_session.get('from_chat_id', 'Unknown')
                session_info = f"Session: {color(session_name, MGA)} | Bot: {color('@'+bot_username, CYN)} | Chat ID: {color(chat_id, YLW)}"
            
            
            from handlers.auto_update_commands import auto_update_threads
            auto_update_count = sum(1 for thread in auto_update_threads.values() if thread.is_alive())
            auto_update_status = f" | Auto-Updates: {color(auto_update_count, GRN)}" if auto_update_count > 0 else ""
            
            
            if session_info:
                status_text = f"{color('MikShaf Ready', GRN)} | {session_info}"
            elif auto_update_status:
                status_text = f"{color('MikShaf Ready', GRN)} | Status:{auto_update_status}"
            else:
                status_text = f"{color('MikShaf Ready', GRN)}"
                
            print(generate_box([status_text], -1))
            
            
            print(generate_box([
                f"{color('1', YLW, f'{DIM}[STR{DIM}]{RST}')} Add Target", 
                f"{color('2', YLW, f'{DIM}[STR{DIM}]{RST}')} Saved Session", 
                f"{color('3', YLW, f'{DIM}[STR{DIM}]{RST}')} Detailed Chat Info", 
                f"{color('I', CYN, f'{DIM}[STR{DIM}]{RST}')} Comprehensive Bot Info",
                f"{color('M', CYN, f'{DIM}[STR{DIM}]{RST}')} Monitor Messages",
                f"{color('A', GRN, f'{DIM}[STR{DIM}]{RST}')} Start Auto-Update",
                f"{color('S', RED, f'{DIM}[STR{DIM}]{RST}')} Stop Auto-Update",
                f"{color('U', BLU, f'{DIM}[STR{DIM}]{RST}')} Auto-Update Status",
                f"{color('4', YLW, f'{DIM}[STR{DIM}]{RST}')} Send Message", 
                f"{color('5', YLW, f'{DIM}[STR{DIM}]{RST}')} Spam Chat", 
                f"{color('6', YLW, f'{DIM}[STR{DIM}]{RST}')} Delete Recent Messages", 
                f"{color('7', YLW, f'{DIM}[STR{DIM}]{RST}')} Download All Messages",
                f"{color('8', YLW, f'{DIM}[STR{DIM}]{RST}')} Forward Messages",
                f"{color('9', YLW, f'{DIM}[STR{DIM}]{RST}')} Send File", 
                f"{color('C', RED, f'{DIM}[STR{DIM}]{RST}')} Clear Current Session",
                f"{color('0', RED, f'{DIM}[STR{DIM}]{RST}')} Exit"
            ], -1, title="Main Menu", titleclr=YLW))

            choice = input(prompt('Select Menu'))
            
            
            if choice == "1":
                from handlers.session_commands import new_dumper
                new_dumper(API_ID=API_ID, API_HASH=API_HASH)
            elif choice == "2":
                from handlers.session_commands import show_sessions
                session = show_sessions(API_ID=API_ID, API_HASH=API_HASH)
                if session:
                    current_session = session
            elif choice == "3":
                from handlers.bot_commands import get_detailed_chat_info
                get_detailed_chat_info(current_session, "telegram_data/mikshaf_session", API_ID, API_HASH)
            elif choice.lower() == "i":
                from handlers.bot_commands import comprehensive_bot_info
                comprehensive_bot_info(current_session)
            elif choice.lower() == "m":
                from handlers.bot_commands import monitor_messages
                monitor_messages(current_session)
            elif choice.lower() == "a":
                from handlers.auto_update_commands import start_auto_update
                start_auto_update(current_session)
            elif choice.lower() == "s":
                from handlers.auto_update_commands import stop_auto_update
                stop_auto_update()
            elif choice.lower() == "u":
                from handlers.auto_update_commands import show_auto_update_status
                show_auto_update_status(background_worker_thread)
            elif choice == "4":
                from handlers.bot_commands import send_message_to_chat
                send_message_to_chat(current_session)
            elif choice == "5":
                from handlers.bot_commands import spam_chat
                spam_chat(current_session, "telegram_data/mikshaf_session", API_ID, API_HASH)
            elif choice == "6":
                from handlers.bot_commands import delete_recent_messages
                delete_recent_messages(current_session, "telegram_data/mikshaf_session", API_ID, API_HASH)
            elif choice == "7":
                from handlers.download_commands import download_all_messages
                download_all_messages(current_session, API_ID, API_HASH)
            elif choice == "8" or choice.lower() == "w":
                from handlers.forward_commands import forward_messages
                forward_messages(current_session)
            elif choice == "9" or choice.lower() == "f":
                from handlers.bot_commands import send_file_to_chat
                send_file_to_chat(current_session, "telegram_data/mikshaf_session", API_ID, API_HASH)
            elif choice.lower() == "c":
                if current_session:
                    current_session = None
                else:
                    print(f"{warning} No active session to clear.")
                    input("\nPress ENTER to continue...")
            elif choice == "0":
                
                stop_background_worker()
                print(f"{info} Exiting MikShaf...")
                sys.exit(0)
            else:
                print(f"{error} Invalid choice, try again.")
                input("\nPress ENTER to continue...")

    except KeyboardInterrupt:
        print(f"\n{info} Exiting...")
        
        
        stop_background_worker()
        sys.exit(0)

if __name__ == "__main__":
    main_menu()
