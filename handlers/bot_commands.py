import json
import os
import sys
import time
import random
import requests
from utils.ui_utils import banner, generate_box, prompt, color, ok, info, success, warning, error
from utils.ui_utils import RED, GRN, YLW, BLU, MGA, CYN, RST, DIM
from utils.telegram_utils import (
    get_bot_info, get_chat_info, get_bot_owner, get_latest_messageid, 
    parse_bot_token, is_bot_online, get_chat_administrators, 
    get_My_Default_AdministratorRights, get_my_commands, get_chat_member_count,
    create_silent_telegram_client, is_telethon_authenticated,
    send_telegram_message, deleteMessage, parse_dict, get_updates,
    send_file_to_telegram_channel
)

def checkbot():
    banner()
    print(generate_box([], -1, "Check Bot Status", titleclr=GRN))
    bot_token = ""
    try:
        while not bot_token:
            bot_token = input(prompt('Bot Token'))
        print("")
    except KeyboardInterrupt:
        return

    data = is_bot_online(bot_token, returnType='raw')
    print(f"\n{RST}{json.dumps(data, indent=4)}")
    input("\nPress ENTER to continue...")

def checkbot_chatid():
    banner()
    print(generate_box([], -1, "Check Bot Chat ID Status", titleclr=GRN))
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

    data = get_bot_owner(bot_token, from_chat_id, returnType='raw')
    print(f"\n{RST}{json.dumps(data, indent=4)}")
    input("\nPress ENTER to continue...")

def get_detailed_chat_info(current_session=None, TELETHON_SESSION=None, API_ID=None, API_HASH=None):
    banner()
    print(generate_box([], -1, "Detailed Chat Info", titleclr=GRN))
    
    bot_token = ""
    chat_id = ""
    
    if current_session:
        bot_token = current_session['bot_token']
        chat_id = current_session['from_chat_id']
        print(f"{info} Using session: {color(current_session.get('session_name', 'Unnamed'), MGA)} ({color('@'+current_session.get('username', 'Unknown'), CYN)})")
    
    try:
        if not bot_token:
            while not bot_token:
                bot_token = input(prompt('Bot Token'))
            print("")
        
        if not chat_id:
            while not chat_id:
                chat_id = input(prompt('Chat ID'))
            print("")
    except KeyboardInterrupt:
        return
    
    bot_token = parse_bot_token(bot_token)
    
    bot_info = is_bot_online(bot_token)
    if not bot_info:
        print(f"{error} Bot is offline or token is invalid. Try again.")
        input("\nPress ENTER to continue...")
        return
    
    print(f"{info} Fetching detailed chat information for chat ID: {color(chat_id, GRN)}...")
    
    try:
        
        chat_data = get_chat_info(bot_token, chat_id)
        
        if not chat_data.get("ok", False):
            print(f"{error} Failed to fetch chat info: {chat_data.get('description', 'Unknown error')}")
            input("\nPress ENTER to continue...")
            return
        
        chat_info = chat_data["result"]
        
        
        admins_data = {"result": []}
        if chat_info.get("type") in ["group", "supergroup", "channel"]:
            admins_data = get_chat_administrators(bot_token, chat_id)
        
        
        members_count = 0
        if chat_info.get("type") in ["group", "supergroup", "channel"]:
            count_data = get_chat_member_count(bot_token, chat_id)
            if count_data.get("ok", False):
                members_count = count_data["result"]
        
        
        telethon_info = {}
        if TELETHON_SESSION and is_telethon_authenticated(TELETHON_SESSION) and API_ID and API_HASH:
                try:
                    from telethon.sync import TelegramClient
                    
                    with create_silent_telegram_client(TELETHON_SESSION, API_ID, API_HASH) as client:
                        client.connect()
                        if client.is_user_authorized():
                            try:
                                entity = client.get_entity(int(chat_id))
                                for attr in dir(entity):
                                    if not attr.startswith('_') and not callable(getattr(entity, attr)):
                                        telethon_info[attr] = getattr(entity, attr)
                            except Exception as e:
                                print(f"{warning} Couldn't get entity: {e}")
                except Exception as e:
                    print(f"{warning} Telethon error: {e}")
        
        
        chat_type = chat_info.get("type", "Unknown").capitalize()
        chat_title = chat_info.get("title", chat_info.get("first_name", "Unknown"))
        
        info_lines = []
        
        
        info_lines.append(f"{ok} {color('Basic Information:', YLW)}")
        info_lines.append(f"{ok} Chat ID: {color(chat_id, YLW)}")
        info_lines.append(f"{ok} Type: {color(chat_type, GRN)}")
        
        if chat_info.get("title"):
            info_lines.append(f"{ok} Title: {color(chat_info['title'], CYN)}")
        
        if chat_info.get("first_name"):
            info_lines.append(f"{ok} First Name: {color(chat_info['first_name'], CYN)}")
        
        if chat_info.get("last_name"):
            info_lines.append(f"{ok} Last Name: {color(chat_info['last_name'], CYN)}")
            
        if chat_info.get("username"):
            info_lines.append(f"{ok} Username: {color('@' + chat_info['username'], BLU)}")
        
        
        if chat_info.get("active_usernames"):
            info_lines.append(f"{ok} Active Usernames:")
            for username in chat_info["active_usernames"]:
                info_lines.append(f"  {ok} @{color(username, BLU)}")
        
        
        if chat_info.get("bio"):
            info_lines.append(f"{ok} Bio: {color(chat_info['bio'], MGA)}")
        if chat_info.get("description"):
            info_lines.append(f"{ok} Description: {color(chat_info['description'], MGA)}")
        
        
        info_lines.append(f"\n{ok} {color('Features and Settings:', YLW)}")
        
        if "can_send_gift" in chat_info:
            gift_status = "Enabled" if chat_info["can_send_gift"] else "Disabled"
            info_lines.append(f"{ok} Can Send Gift: {color(gift_status, GRN if chat_info['can_send_gift'] else RED)}")
        
        if "accepted_gift_types" in chat_info:
            info_lines.append(f"{ok} Accepted Gift Types:")
            for gift_type, enabled in chat_info["accepted_gift_types"].items():
                status = "Enabled" if enabled else "Disabled"
                info_lines.append(f"  {ok} {gift_type.replace('_', ' ').title()}: {color(status, GRN if enabled else RED)}")
        
        if "max_reaction_count" in chat_info:
            info_lines.append(f"{ok} Max Reaction Count: {color(str(chat_info['max_reaction_count']), YLW)}")
            
        if "accent_color_id" in chat_info:
            info_lines.append(f"{ok} Accent Color ID: {color(str(chat_info['accent_color_id']), YLW)}")
        
        
        if "permissions" in chat_info:
            info_lines.append(f"\n{ok} {color('Chat Permissions:', YLW)}")
            for perm, value in chat_info["permissions"].items():
                status = "Allowed" if value else "Restricted"
                info_lines.append(f"{ok} {perm.replace('can_', '').replace('_', ' ').title()}: {color(status, GRN if value else RED)}")
        
        
        if members_count:
            info_lines.append(f"\n{ok} {color('Member Information:', YLW)}")
            info_lines.append(f"{ok} Total Members: {color(str(members_count), GRN)}")
        
        
        if chat_info.get("invite_link"):
            info_lines.append(f"\n{ok} {color('Invite Information:', YLW)}")
            info_lines.append(f"{ok} Invite Link: {color(chat_info['invite_link'], BLU)}")
        
        
        if telethon_info:
            info_lines.append(f"\n{ok} {color('Additional Telethon Information:', YLW)}")
            for key, value in telethon_info.items():
                if key not in ["id", "access_hash"] and value is not None:
                    if isinstance(value, (list, tuple)) and value:
                        info_lines.append(f"{ok} {key.replace('_', ' ').title()}: {color(', '.join(map(str, value)), YLW)}")
                    elif isinstance(value, dict) and value:
                        info_lines.append(f"{ok} {key.replace('_', ' ').title()}:")
                        for k, v in value.items():
                            info_lines.append(f"  {ok} {k.replace('_', ' ').title()}: {color(str(v), YLW)}")
                    elif isinstance(value, bool):
                        status = "Yes" if value else "No"
                        info_lines.append(f"{ok} {key.replace('_', ' ').title()}: {color(status, GRN if value else RED)}")
                    else:
                        info_lines.append(f"{ok} {key.replace('_', ' ').title()}: {color(str(value), YLW)}")
        
        
        if admins_data.get("ok") and admins_data.get("result"):
            info_lines.append(f"\n{ok} {color('Administrators:', YLW)}")
            for admin in admins_data["result"]:
                user = admin["user"]
                name = user.get("first_name", "")
                if user.get("last_name"):
                    name += f" {user['last_name']}"
                
                username = f" (@{user['username']})" if user.get("username") else ""
                status = admin.get("status", "admin")
                
                info_lines.append(f"{ok} {color(name, CYN)}{color(username, BLU)} - {color(status.title(), GRN if status == 'creator' else YLW)}")
                
                
                if "can_be_edited" in admin:
                    perms = []
                    for perm, value in admin.items():
                        if perm.startswith("can_") and perm != "can_be_edited" and value is True:
                            perms.append(perm.replace("can_", "").replace("_", " "))
                    
                    if perms:
                        info_lines.append(f"  {ok} Permissions: {color(', '.join(perms), CYN)}")
        
        
        info_lines.append(f"\n{ok} {color('Raw JSON data:', YLW)} (saved to ./chats/chat_info_{chat_id}.json)")
        
        
        if not os.path.exists("chats"):
            os.makedirs("chats")
            
        
        with open(f"chats/chat_info_{chat_id}.json", "w") as f:
            json.dump(chat_data, f, indent=4)
        
        print(generate_box(info_lines, -1, title="Chat Information", titleclr=MGA, pos="left"))
        
    except Exception as e:
        print(f"{error} An error occurred: {str(e)}")
    
    input("\nPress ENTER to continue...")

def comprehensive_bot_info(current_session=None):
    banner()
    print(generate_box([], -1, "Comprehensive Bot Info", titleclr=GRN))
    
    bot_token = ""
    
    if current_session:
        bot_token = current_session['bot_token']
        print(f"{info} Using session: {color(current_session.get('session_name', 'Unnamed'), MGA)} ({color('@'+current_session.get('username', 'Unknown'), CYN)})")
    
    try:
        if not bot_token:
            while not bot_token:
                bot_token = input(prompt('Bot Token'))
            print("")
    except KeyboardInterrupt:
        return
    
    bot_token = parse_bot_token(bot_token)
    
    print(f"{info} Fetching comprehensive information for bot...")
    
    try:
        
        bot_data = get_bot_info(bot_token)
        
        if not bot_data.get("ok", False):
            print(f"{error} Failed to fetch bot info: {bot_data.get('description', 'Unknown error')}")
            input("\nPress ENTER to continue...")
            return
        
        
        commands_data = get_my_commands(None, bot_token)
        
        
        bot_info = bot_data["result"]
        
        info_lines = []
        info_lines.append(f"{ok} {color('Bot Information:', YLW)}")
        info_lines.append(f"{ok} ID: {color(str(bot_info.get('id', 'Unknown')), YLW)}")
        info_lines.append(f"{ok} Name: {color(bot_info.get('first_name', 'Unknown'), CYN)}")
        info_lines.append(f"{ok} Username: {color('@' + bot_info.get('username', 'Unknown'), BLU)}")
        
        
        if commands_data.get("ok", False) and commands_data.get("result"):
            info_lines.append(f"\n{ok} {color('Bot Commands:', YLW)}")
            for cmd in commands_data["result"]:
                info_lines.append(f"{ok} /{color(cmd.get('command', ''), GRN)} - {cmd.get('description', 'No description')}")
        
        
        bot_username = bot_info.get('username', 'unknown')
        with open(f"bot_info_{bot_username}.json", "w") as f:
            json.dump(bot_data, f, indent=4)
        
        info_lines.append(f"\n{ok} Raw data saved to: bot_info_{bot_username}.json")
        
        print(generate_box(info_lines, -1, title="Bot Information", titleclr=MGA, pos="left"))
        
    except Exception as e:
        print(f"{error} An error occurred: {str(e)}")
    
    input("\nPress ENTER to continue...")

def monitor_messages(current_session=None):
    banner()
    print(generate_box([], -1, "Monitor Messages", titleclr=GRN))
    
    bot_token = ""
    
    if current_session:
        bot_token = current_session['bot_token']
        print(f"{info} Using session: {color(current_session.get('session_name', 'Unnamed'), MGA)} ({color('@'+current_session.get('username', 'Unknown'), CYN)})")
    
    try:
        if not bot_token:
            while not bot_token:
                bot_token = input(prompt('Bot Token'))
            print("")
    except KeyboardInterrupt:
        return
    
    bot_token = parse_bot_token(bot_token)
    
    print(f"{info} Starting message monitor. Press Ctrl+C to stop.")
    print(f"{info} Waiting for new messages...")
    
    try:
        offset = None
        while True:
            updates = get_updates(bot_token, offset)
            
            if updates.get("ok", False) and updates.get("result"):
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    
                    if "message" in update:
                        message = update["message"]
                        chat = message.get("chat", {})
                        from_user = message.get("from", {})
                        
                        chat_type = chat.get("type", "Unknown")
                        chat_id = chat.get("id", "Unknown")
                        
                        if chat_type == "private":
                            chat_name = f"{chat.get('first_name', '')} {chat.get('last_name', '')}".strip()
                        else:
                            chat_name = chat.get("title", "Unknown")
                        
                        user_name = f"{from_user.get('first_name', '')} {from_user.get('last_name', '')}".strip()
                        user_id = from_user.get("id", "Unknown")
                        username = from_user.get("username", "None")
                        
                        message_text = message.get("text", "")
                        
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                        
                        print(f"\n{timestamp}")
                        print(f"Chat: {color(chat_name, CYN)} ({color(chat_id, YLW)}) [{color(chat_type, GRN)}]")
                        print(f"From: {color(user_name, MGA)} ({color(user_id, YLW)}) [@{color(username, BLU)}]")
                        print(f"Message: {color(message_text, RST)}")
                        
                        
                        log_dir = os.path.join("logs", "monitor")
                        if not os.path.exists(log_dir):
                            os.makedirs(log_dir)
                        
                        with open(os.path.join(log_dir, f"messages_{chat_id}.log"), "a") as f:
                            f.write(f"[{timestamp}] From: {user_name} (@{username}) [{user_id}]: {message_text}\n")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n{info} Message monitoring stopped.")
    except Exception as e:
        print(f"\n{error} An error occurred: {str(e)}")
    
    input("\nPress ENTER to continue...")

def send_message_to_chat(current_session=None):
    banner()
    print(generate_box([], -1, "Send Message to Chat", titleclr=GRN))
    
    bot_token = ""
    chat_id = ""
    
    if current_session:
        bot_token = current_session['bot_token']
        chat_id = current_session['from_chat_id']
        print(f"{info} Using session: {color(current_session.get('session_name', 'Unnamed'), MGA)} ({color('@'+current_session.get('username', 'Unknown'), CYN)})")
    
    try:
        if not bot_token:
            while not bot_token:
                bot_token = input(prompt('Bot Token'))
            print("")
        
        if not chat_id:
            while not chat_id:
                chat_id = input(prompt('Chat ID'))
            print("")
        
        message = input(prompt('Message to Send'))
        print("")
        
    except KeyboardInterrupt:
        return
    
    bot_token = parse_bot_token(bot_token)
    
    bot_info = is_bot_online(bot_token)
    if not bot_info:
        print(f"{error} Bot is offline or token is invalid. Try again.")
        input("\nPress ENTER to continue...")
        return
    
    print(f"{info} Sending message to chat ID: {color(chat_id, GRN)}...")
    
    try:
        
        response = send_telegram_message(bot_token, chat_id, message)
        
        if response.get("ok", False):
            print(f"{success} Message sent successfully!")
            print(f"{ok} Message ID: {color(response['result']['message_id'], GRN)}")
        else:
            print(f"{error} Failed to send message: {response.get('description', 'Unknown error')}")
        
    except Exception as e:
        print(f"{error} An error occurred: {e}")
    
    input("\nPress ENTER to continue...")

def spam_chat(current_session=None, TELETHON_SESSION=None, API_ID=None, API_HASH=None):
    banner()
    print(generate_box([], -1, "Spam Chat", titleclr=RED))
    
    bot_token = ""
    chat_id = ""
    
    if current_session:
        bot_token = current_session['bot_token']
        chat_id = current_session['from_chat_id']
        print(f"{info} Using session: {color(current_session.get('session_name', 'Unnamed'), MGA)} ({color('@'+current_session.get('username', 'Unknown'), CYN)})")
    
    try:
        if not bot_token:
            while not bot_token:
                bot_token = input(prompt('Bot Token'))
            print("")
        
        if not chat_id:
            while not chat_id:
                chat_id = input(prompt('Chat ID'))
            print("")
        
        message = input(prompt('Spam Message'))
        print("")
        
        count = input(prompt('Number of Messages (default: 10)'))
        if not count.isdigit():
            count = 10
        else:
            count = int(count)
        print("")
        
        delay = input(prompt('Delay Between Messages in seconds (default: 0.5)'))
        if not delay.replace('.', '').isdigit():
            delay = 0.5
        else:
            delay = float(delay)
        print("")
        
    except KeyboardInterrupt:
        return
    
    bot_token = parse_bot_token(bot_token)
    
    bot_info = is_bot_online(bot_token)
    if not bot_info:
        print(f"{error} Bot is offline or token is invalid. Try again.")
        input("\nPress ENTER to continue...")
        return
    
    print(f"{warning} About to send {color(count, RED)} messages to chat ID: {color(chat_id, GRN)}")
    confirm = input(f"{warning} Are you sure you want to continue? (y/N): ")
    
    if confirm.lower() != 'y':
        print(f"{info} Operation cancelled.")
        input("\nPress ENTER to continue...")
        return
    
    print(f"{info} Starting spam operation...")
    
    try:
        success_count = 0
        failed_count = 0
        
        for i in range(1, count + 1):
            message_to_send = f"{message} [{i}/{count}]"
            
            response = send_telegram_message(bot_token, chat_id, message_to_send)
            
            if response.get("ok", False):
                success_count += 1
            else:
                failed_count += 1
                print(f"\n{error} Failed to send message {i}: {response.get('description', 'Unknown error')}")
            
            progress = (i / count) * 100
            sys.stdout.write(
                f"\r{ok} Progress: {color(f'{progress:.1f}%', YLW)} "
                f"[{color(i, YLW)}/{color(count, GRN)}] "
                f"[Success: {color(success_count, GRN)}] "
                f"[Failed: {color(failed_count, RED)}]"
            )
            sys.stdout.flush()
            
            time.sleep(delay)
        
        print(f"\n\n{success} Spam operation completed!")
        print(f"{ok} Messages sent: {color(success_count, GRN)}")
        print(f"{ok} Failed: {color(failed_count, RED)}")
        
    except KeyboardInterrupt:
        print(f"\n{warning} Operation interrupted.")
        print(f"{info} Messages sent: {color(success_count, GRN)}")
    except Exception as e:
        print(f"\n{error} An error occurred: {e}")
    
    input("\nPress ENTER to continue...")

def delete_recent_messages(current_session=None, TELETHON_SESSION=None, API_ID=None, API_HASH=None):
    banner()
    print(generate_box([], -1, "Delete Recent Messages", titleclr=RED))
    
    bot_token = ""
    chat_id = ""
    
    if current_session:
        bot_token = current_session['bot_token']
        chat_id = current_session['from_chat_id']
        print(f"{info} Using session: {color(current_session.get('session_name', 'Unnamed'), MGA)} ({color('@'+current_session.get('username', 'Unknown'), CYN)})")
    
    try:
        if not bot_token:
            while not bot_token:
                bot_token = input(prompt('Bot Token'))
            print("")
        
        if not chat_id:
            while not chat_id:
                chat_id = input(prompt('Chat ID'))
            print("")
    except KeyboardInterrupt:
        return
    
    bot_token = parse_bot_token(bot_token)
    
    bot_info = is_bot_online(bot_token)
    if not bot_info:
        print(f"{error} Bot is offline or token is invalid. Try again.")
        input("\nPress ENTER to continue...")
        return
    
    
    print(f"{info} Fetching most recent message ID...")
    latest_id = get_latest_messageid(bot_token, chat_id)
    
    if not latest_id:
        print(f"{error} Could not determine the latest message ID.")
        input("\nPress ENTER to continue...")
        return
    
    print(f"{ok} Latest message ID: {color(latest_id, GRN)}")
    
    
    count = input(prompt('Number of Messages to Delete (default: 10)'))
    if not count.isdigit():
        count = 10
    else:
        count = int(count)
    print("")
    
    
    start_id = latest_id - count + 1
    if start_id < 1:
        start_id = 1
    
    print(f"{warning} About to delete {color(latest_id - start_id + 1, RED)} messages from chat ID: {color(chat_id, GRN)}")
    print(f"{info} Message IDs to delete: {color(start_id, YLW)} to {color(latest_id, YLW)}")
    
    confirm = input(f"{warning} Are you sure you want to continue? (y/N): ")
    
    if confirm.lower() != 'y':
        print(f"{info} Operation cancelled.")
        input("\nPress ENTER to continue...")
        return
    
    print(f"{info} Starting deletion operation...")
    
    try:
        success_count = 0
        failed_count = 0
        
        for message_id in range(latest_id, start_id - 1, -1):
            response = deleteMessage(bot_token, chat_id, message_id)
            
            if response.get("ok", False):
                success_count += 1
            else:
                failed_count += 1
                if response.get("description") != "Bad Request: message can't be deleted":
                    print(f"\n{error} Failed to delete message {message_id}: {response.get('description', 'Unknown error')}")
            
            progress = ((latest_id - message_id + 1) / (latest_id - start_id + 1)) * 100
            sys.stdout.write(
                f"\r{ok} Progress: {color(f'{progress:.1f}%', YLW)} "
                f"[{color(latest_id - message_id + 1, YLW)}/{color(latest_id - start_id + 1, GRN)}] "
                f"[Deleted: {color(success_count, GRN)}] "
                f"[Failed: {color(failed_count, RED)}]"
            )
            sys.stdout.flush()
            
            time.sleep(0.2)  
        
        print(f"\n\n{success} Deletion operation completed!")
        print(f"{ok} Messages deleted: {color(success_count, GRN)}")
        print(f"{ok} Failed: {color(failed_count, RED)}")
        
    except KeyboardInterrupt:
        print(f"\n{warning} Operation interrupted.")
        print(f"{info} Messages deleted: {color(success_count, GRN)}")
    except Exception as e:
        print(f"\n{error} An error occurred: {e}")
    
    input("\nPress ENTER to continue...")

def send_file_to_chat(current_session=None, TELETHON_SESSION=None, API_ID=None, API_HASH=None):
    banner()
    print(generate_box([], -1, "Send File to Chat", titleclr=GRN))
    
    bot_token = ""
    chat_id = ""
    
    if current_session:
        bot_token = current_session['bot_token']
        chat_id = current_session['from_chat_id']
        print(f"{info} Using session: {color(current_session.get('session_name', 'Unnamed'), MGA)} ({color('@'+current_session.get('username', 'Unknown'), CYN)})")
    
    try:
        if not bot_token:
            while not bot_token:
                bot_token = input(prompt('Bot Token'))
            print("")
        
        if not chat_id:
            while not chat_id:
                chat_id = input(prompt('Chat ID'))
            print("")
        
        file_path = input(prompt('File Path'))
        if not os.path.exists(file_path):
            print(f"{error} File not found: {file_path}")
            input("\nPress ENTER to continue...")
            return
        print("")
        
    except KeyboardInterrupt:
        return
    
    bot_token = parse_bot_token(bot_token)
    
    bot_info = is_bot_online(bot_token)
    if not bot_info:
        print(f"{error} Bot is offline or token is invalid. Try again.")
        input("\nPress ENTER to continue...")
        return
    
    print(f"{info} Sending file to chat ID: {color(chat_id, GRN)}...")
    
    try:
        response = send_file_to_telegram_channel(bot_token, chat_id, file_path)
        
        if response and response.get("ok", False):
            print(f"{success} File sent successfully!")
            print(f"{ok} Message ID: {color(response['result']['message_id'], GRN)}")
        else:
            print(f"{error} Failed to send file: {response.get('description', 'Unknown error') if response else 'No response'}")
        
    except Exception as e:
        print(f"{error} An error occurred: {e}")
    
    input("\nPress ENTER to continue...")
