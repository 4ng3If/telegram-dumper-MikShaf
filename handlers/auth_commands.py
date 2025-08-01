import os
import json
from utils.ui_utils import banner, generate_box, prompt, color, ok, info, success, warning, error
from utils.ui_utils import RED, GRN, YLW, BLU, MGA, CYN, RST, DIM
from utils.telegram_utils import create_silent_telegram_client
from telethon.errors import SessionPasswordNeededError

def init(SRC_PATH=None, SESSION_DIR=None, ENV_FILE=None):
    from utils.session_manager import SessionManager
    from dotenv import load_dotenv
    
    if SRC_PATH is None:
        SRC_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'telegram_data')
    
    if SESSION_DIR is None:
        SESSION_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "telegram_data", "bot_sessions")
    
    if ENV_FILE is None:
        ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    
    for directory in [SRC_PATH, SESSION_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    session_mgr = SessionManager(SESSION_DIR)
    
    session_mgr.clean_duplicate_sessions()
    session_mgr.migrate_sessions()

    SESSION_FILE = os.path.join(SRC_PATH, "session.json")
    if not os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "w") as f:
            f.write("{}")
            f.close()
    if not os.path.exists(ENV_FILE):
        envs = []
        inputs = input("Enter Telegram API_ID: ")
        envs.append(f"API_ID = {inputs}")
        inputs = input("Enter Telegram API_HASH: ")
        envs.append(f"API_HASH = {inputs}")
        inputs = input("Enter The Receiver Chat ID: ")
        envs.append(f"TO_CHAT_ID = {inputs}")

        with open(ENV_FILE, "w") as f:
            f.write("\n".join(envs))
            f.close()
    
    load_dotenv()
    TO_CHAT_ID = os.getenv("TO_CHAT_ID")
    API_ID = os.getenv("API_ID")
    API_HASH = os.getenv("API_HASH")

    if not TO_CHAT_ID or not API_ID or not API_HASH:
        print(f"{warning} Some environment variables (TO_CHAT_ID, API_ID, API_HASH) are missing.")
        print(f"{info} Telethon features will not be available until you configure them.")
    
    return TO_CHAT_ID, API_ID, API_HASH

def authenticate_telethon(API_ID=None, API_HASH=None, TELETHON_SESSION=None, current_session=None):
    from dotenv import load_dotenv
    from utils.session_manager import SessionManager
    
    if TELETHON_SESSION is None:
        TELETHON_SESSION = os.path.join(os.path.dirname(os.path.dirname(__file__)), "telegram_data", "mikshaf_session")
    
    if API_ID is None or API_HASH is None:
        load_dotenv()
        API_ID = os.getenv("API_ID")
        API_HASH = os.getenv("API_HASH")
    
    if not API_ID or not API_HASH:
        print(f"{warning} Please set API_ID and API_HASH in the .env file first.")
        return False

    print(f"{info} Logging in to Telegram...")
    
    client = create_silent_telegram_client(TELETHON_SESSION, API_ID, API_HASH)

    with client:
        client.connect()
        if not client.is_user_authorized():
            if current_session and 'bot_token' in current_session:
                bot_token = current_session['bot_token']
                session_name = current_session.get('session_name', 'current session')
                print(f"{info} Using bot token from {color(session_name, MGA)}...")
                try:
                    client.sign_in(bot_token=bot_token)
                    print(f"{success} Login successful! Telethon session saved.")
                    
                    session_mgr = SessionManager(os.path.join(os.path.dirname(os.path.dirname(__file__)), "session"))
                    session_mgr.display_session_dashboard()
                    return True
                except Exception as e:
                    print(f"{warning} Failed to authenticate with the bot token from current session: {e}")
                    print(f"{info} Falling back to manual authentication...")
            
            phone_or_token = input(f"{ok} Please enter your phone (or bot token): ")
            
            if ":" in phone_or_token:
                try:
                    client.sign_in(bot_token=phone_or_token)
                    print(f"{success} Login successful with bot token! Telethon session saved.")
                    
                    session_mgr = SessionManager(os.path.join(os.path.dirname(os.path.dirname(__file__)), "session"))
                    session_mgr.display_session_dashboard()
                    return True
                except Exception as e:
                    print(f"{error} Bot token login failed: {e}")
                    return False
            else:
                try:
                    client.send_code_request(phone_or_token)
                    code = input(f"{ok} Enter the confirmation code: ")
                    try:
                        client.sign_in(phone_or_token, code)
                        print(f"{success} Login successful! Telethon session saved.")
                    except SessionPasswordNeededError:
                        password = input(f"{ok} Enter your 2FA password: ")
                        client.sign_in(password=password)
                        print(f"{success} Login successful with 2FA! Telethon session saved.")
                    
                    session_mgr = SessionManager(os.path.join(os.path.dirname(os.path.dirname(__file__)), "session"))
                    session_mgr.display_session_dashboard()
                    return True
                except Exception as e:
                    print(f"{error} Login failed: {e}")
                    return False
        else:
            print(f"{success} Already logged in with Telethon.")
            
            session_mgr = SessionManager(os.path.join(os.path.dirname(os.path.dirname(__file__)), "session"))
            session_mgr.display_session_dashboard()
            return True
