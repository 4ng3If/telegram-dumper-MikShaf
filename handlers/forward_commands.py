import os
import sys
import time
from utils.ui_utils import banner, generate_box, prompt, color, ok, info, success, warning, error
from utils.ui_utils import RED, GRN, YLW, BLU, MGA, CYN, RST, DIM
from utils.telegram_utils import parse_bot_token, is_bot_online, get_latest_messageid, forward_msg

def forward_messages(current_session=None):
    banner()
    print(generate_box([], -1, "Forward Messages", titleclr=GRN))
    
    source_bot_token = ""
    source_chat_id = ""
    target_chat_id = ""
    
    try:
        if current_session:
            source_bot_token = current_session['bot_token']
            source_chat_id = current_session['from_chat_id']
            print(f"{info} Using session: {color(current_session.get('session_name', 'Unnamed'), MGA)} ({color('@'+current_session.get('username', 'Unknown'), CYN)})")
        
        if not source_bot_token:
            while not source_bot_token:
                source_bot_token = input(prompt('Source Bot Token'))
            source_bot_token = parse_bot_token(source_bot_token)
            print("")
            
            bot_info = is_bot_online(source_bot_token)
            if not bot_info:
                print(f"{error} Bot is offline or token is invalid. Try again.")
                input("\nPress ENTER to continue...")
                return
        
        if not source_chat_id:
            while not source_chat_id:
                source_chat_id = input(prompt('Source Chat ID'))
            print("")
        
        while not target_chat_id:
            target_chat_id = input(prompt('Target Chat ID (where to forward to)'))
        print("")
        
        print(f"{info} Fetching latest message ID from source chat...")
        latest_id = get_latest_messageid(source_bot_token, source_chat_id)
        
        if latest_id is None or latest_id <= 1:
            print(f"{warning} Could not determine last message ID.")
            latest_id = input(prompt('Enter Last Message ID manually'))
            if not latest_id.isdigit():
                print(f"{error} Invalid message ID.")
                input("\nPress ENTER to continue...")
                return
            latest_id = int(latest_id)
        
        print(f"{ok} Latest message ID: {color(latest_id, GRN)}")
        
        start_id = input(prompt('Start Message ID'))
        if not start_id.isdigit():
            print(f"{error} Invalid message ID.")
            input("\nPress ENTER to continue...")
            return
        start_id = int(start_id)
        
        end_id = input(prompt('End Message ID (default: latest)'))
        if not end_id.strip():
            end_id = latest_id
        elif not end_id.isdigit():
            print(f"{error} Invalid message ID.")
            input("\nPress ENTER to continue...")
            return
        end_id = int(end_id)
        
        if start_id > end_id:
            print(f"{warning} Start ID is greater than End ID. Swapping values.")
            start_id, end_id = end_id, start_id
        
        if end_id - start_id + 1 > 100:
            print(f"{warning} You're trying to forward {color(end_id - start_id + 1, RED)} messages.")
            confirm = input(f"{warning} Are you sure you want to continue? (y/N): ")
            if confirm.lower() != 'y':
                print(f"{info} Operation cancelled.")
                input("\nPress ENTER to continue...")
                return
        
        print(f"{info} About to forward messages from {color(start_id, YLW)} to {color(end_id, YLW)}")
        print(f"{info} Source chat: {color(source_chat_id, GRN)}")
        print(f"{info} Target chat: {color(target_chat_id, GRN)}")
        
        confirm = input(f"{warning} Continue? (Y/n): ")
        if confirm.lower() == 'n':
            print(f"{info} Operation cancelled.")
            input("\nPress ENTER to continue...")
            return
        
        print(f"{info} Starting message forwarding...")
        
        success_count = 0
        failed_count = 0
        
        total_messages = end_id - start_id + 1
        
        for message_id in range(start_id, end_id + 1):
            progress = ((message_id - start_id + 1) / total_messages) * 100
            sys.stdout.write(f"\r{ok} Progress: {color(f'{progress:.1f}%', YLW)} [{color(message_id - start_id + 1, YLW)}/{color(total_messages, GRN)}]")
            sys.stdout.flush()
            
            result = forward_msg(source_bot_token, source_chat_id, target_chat_id, message_id)
            
            if result and result.get("ok", False):
                success_count += 1
                time.sleep(0.05)
            else:
                failed_count += 1
                error_msg = result.get("description", "Unknown error") if result else "Request failed"
                
                if failed_count <= 3:
                    sys.stdout.write(f"\n{error} Failed to forward message {message_id}: {error_msg}")
                    sys.stdout.flush()
        
        print(f"\n\n{success} Forward operation completed!")
        print(f"{ok} Total messages forwarded: {color(success_count, GRN)}")
        print(f"{ok} Failed forwards: {color(failed_count, RED)}")
        
    except KeyboardInterrupt:
        print(f"\n{warning} Operation interrupted.")
        print(f"{ok} Messages forwarded: {color(success_count, GRN)}")
        print(f"{ok} Failed forwards: {color(failed_count, RED)}")
    except Exception as e:
        print(f"\n{error} An error occurred: {e}")
    
    input("\nPress ENTER to continue...")
