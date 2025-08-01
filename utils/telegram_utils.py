import requests
import os
import json
import time
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError

def create_silent_telegram_client(session_name, api_id, api_hash):
    """Create a TelegramClient instance with reduced logging output"""
    return TelegramClient(
        session_name, 
        api_id, 
        api_hash,
        system_version="Silent Mode",
        device_model="Silent Mode",
        app_version="Silent Mode",
        flood_sleep_threshold=60  
    )

def send_telegram_message(bot_token, chat_id, message):
    """Send a message to a Telegram chat using bot API"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    return response.json()

def parse_dict(title, dictionary):
    result = f"{title}:\n"
    for key, value in dictionary.items():
        if isinstance(value, dict):
            result += '\n'.join(f"- {k}: {v}" for k, v in value.items())
        else:
            result += f"- {key}: {value}\n"
    return result + "\n"

def delete_messages(bot_token, chat_id, message_id):
    try:
        response = deleteMessage(bot_token, chat_id, message_id)
        if response.get("ok") == True:
            print(f"Deleted message {message_id}")
            message_id -= 1
        elif response.get("ok") == False and response.get("description") == "Bad Request: message can't be deleted for everyone":
            print(f"Message {message_id} is an old message. You can only delete messages that are within 24 hours.")
        elif response.get("ok") == False:
            print(f"Message {message_id} not found.")
    except Exception as e:
        print(f"Error: {message_id}")

def deleteMessage(bot_token, chat_id, message_id):
    url = f"https://api.telegram.org/bot{bot_token}/deleteMessage"
    data = {"chat_id": chat_id, "message_id": message_id}
    response = requests.post(url, data=data)
    return response.json()

def send_file_to_telegram_channel(bot_token, chat_id, file_path):
    try:
        import mimetypes
        mime_type = mimetypes.guess_type(file_path)[0]
        file_type = 'document'  

        if mime_type:
            if 'audio' in mime_type:
                file_type = 'audio'
            elif 'video' in mime_type:
                file_type = 'video'
            elif 'image' in mime_type:
                file_type = 'photo'

        file_type_methods = {
            'document': 'sendDocument',
            'photo': 'sendPhoto',
            'audio': 'sendAudio',
            'video': 'sendVideo',
            'animation': 'sendAnimation',
            'voice': 'sendVoice',
            'video_note': 'sendVideoNote'
        }

        url = f"https://api.telegram.org/bot{bot_token}/{file_type_methods[file_type]}"
        with open(file_path, 'rb') as file:
            files = {
                file_type: file
            }
            message = input("Enter the message to send with the file (press enter to skip): ")
            data = {
                'chat_id': chat_id,
                'caption': message
            }
            response = requests.post(url, files=files, data=data)
            return response.json()
    except Exception as e:
        print(f"An error occurred while trying to send the file: {e}")

def get_my_commands(chat_id, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/getMyCommands"
    data = {"chat_id": chat_id}
    response = requests.get(url, data=data)
    return response.json()

def get_updates(bot_token, offset=None, timeout=30):
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates?timeout={timeout}"
    if offset:
        url += f"&offset={offset}"
    response = requests.get(url)
    return response.json()

def get_bot_info(bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    response = requests.get(url)
    return response.json()

def get_My_Default_AdministratorRights(bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/getMyDefaultAdministratorRights"
    data = {"chat_id": chat_id}
    response = requests.get(url, data=data)
    return response.json()

def get_chat_info(bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/getChat"
    data = {"chat_id": chat_id}
    response = requests.post(url, data=data)
    return response.json()

def get_chat_administrators(bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/getChatAdministrators"
    data = {"chat_id": chat_id}
    response = requests.post(url, data=data)
    return response.json()

def get_chat_member_count(bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/getChatMembersCount"
    data = {"chat_id": chat_id}
    response = requests.post(url, data=data)
    return response.json()

def get_latest_messageid(bot_token, chat_id):
    response = send_telegram_message(bot_token, chat_id, ".")
    if response.get("ok") == True:
        message_id = response.get('result').get('message_id')
        deleteMessage(bot_token, chat_id, message_id)
        return message_id
    else:
        print("Error: Unable to retrieve latest message id: ",
              response.get("description"))
        return None

def check_file_for_token_and_chat_id(file_path, bot_token, chat_id):
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip() == f"{bot_token}:{chat_id}":
                return True
    return False

def add_token_and_chat_id_to_file(file_path, bot_token, chat_id):
    with open(file_path, 'a') as file:
        file.write(f"{bot_token}:{chat_id}\n")

def parse_bot_token(raw_token):
    raw_token = raw_token.strip()
    if raw_token.lower().startswith("bot"):
        raw_token = raw_token[3:]
    return raw_token

def forward_msg(bot_token, from_chat_id, to_chat_id, message_id):
    url = f"https://api.telegram.org/bot{bot_token}/forwardMessage"
    payload = {
        "from_chat_id": from_chat_id,
        "chat_id": to_chat_id,
        "message_id": message_id
    }
    try:
        r = requests.post(url, json=payload)
        data = r.json()
        return data
    except Exception as e:
        print(f"Forward error: {e}")
        return False

def is_bot_online(bot_token, returnType='filter'):
    bot_token = parse_bot_token(bot_token)
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    try:
        r = requests.get(url)
        data = r.json()
        if returnType == 'raw':
            return data
        if data.get("ok", False):
            return data["result"]
        else:
            print(f"Bot is offline or invalid token: {data}")
            return None
    except Exception as e:
        print(f"Error checking bot status: {e}")
        return None

def get_bot_owner(bot_token, chat_id, returnType='filter'):
    bot_token = parse_bot_token(bot_token)
    url = f"https://api.telegram.org/bot{bot_token}/getChat?chat_id={chat_id}"
    r = requests.get(url)
    data = r.json()

    if returnType == 'raw':
        return data

    if data.get("ok", False):
        return {
            "first": data["result"].get("first_name", "Unknown"),
            "last": data["result"].get("last_name", ""),
            "type": data["result"].get("type", "Unknown")
        }
    else:
        return {
            "first": "Unknown",
            "last": "",
            "type": "Unknown"
        }

def telethon_send_start(bot_token, TELETHON_SESSION, API_ID, API_HASH):
    bot_token = parse_bot_token(bot_token)

    with create_silent_telegram_client(TELETHON_SESSION, API_ID, API_HASH) as client:
        client.connect()

        bot_info = is_bot_online(parse_bot_token(bot_token))
        if not bot_info:
            print(f"Bot is offline. Try again.")
            return

        bot_username = bot_info.get("username", "Unknown")
        print(f"Logged in with your account.")

        try:
            if not bot_username.startswith("@"):
                bot_username = "@" + bot_username
            
            client.send_message(bot_username, "/start")
            print(f"'/start' sent to {bot_username}.")
        except Exception as e:
            print(f"Send error: {e}")
        finally:
            client.disconnect()  

def is_telethon_authenticated(TELETHON_SESSION):
    return os.path.exists(f"{TELETHON_SESSION}.session")
