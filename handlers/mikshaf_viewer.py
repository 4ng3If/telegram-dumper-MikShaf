import os
import random
import pyrogram
import asyncio

def get_file_info(data):
    media_type = ""
    random_numbers = [random.randint(1, 100) for _ in range(6)]
    if data.media is not None:
        try:
            for key in ['document', 'photo', 'video', 'location', 'voice', 'audio']:
                if key in str(data):
                    media_type = key
                    break
            if media_type == "document":
                return (data.document.file_id, data.document.file_name)
            elif media_type == "photo":
                return (data.photo.file_id, f"{random_numbers}.png")
            elif media_type == "video":
                return (data.video.file_id, data.video.file_name)
            elif media_type == "location":
                return (data.location.file_id, data.location.file_name)
            elif media_type == "voice":
                return (data.voice.file_id, data.voice.file_name)
            elif media_type == "audio":
                return (data.audio.file_id, data.audio.file_name)
            else:
                return (None, None)
        except Exception as e:
            print(f"Error: {e}")
            return (None, None)


def parse_and_print_message(message):
    print("=" * 20 + "\n")
    message_dict = message.__dict__
    for key, value in message_dict.items():
        if value not in [None, False]:
            print(f"{key}: {value}")
    print("\n")
    print("=" * 20 + "\n")


def process_messages(bot_token, chat_id, num_messages, message_id, API_ID, API_HASH):
    
    directory = f'telegram_data/user_sessions/{chat_id}'
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    
    download_dir = f'Downloads/{chat_id}'
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    
    logs_dir = f'Downloads/{chat_id}/logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    
    
    user_session_filename = f"{directory}/user_session.session"
    
    
    
    app = pyrogram.Client(user_session_filename, API_ID, API_HASH, bot_token=bot_token)

    async def main(num_messages, message_id):
        try:
            
            counter = message_id - num_messages
            while message_id >= counter:
                message_id -= 1
                async with app:
                    try:
                        
                        numeric_chat_id = int(chat_id)
                        messages = await app.get_messages(numeric_chat_id, message_id)
                    except (ValueError, TypeError):
                        
                        messages = await app.get_messages(chat_id, message_id)
                        
                    if messages.date is None:
                        
                        if message_id % 10 == 0:
                            print(f"[-] Message_id {message_id} not found")
                        counter -= 1
                        pass
                    else:
                        parse_and_print_message(messages)
                        if messages.media is not None:
                            file_id, file_name = get_file_info(messages)
                            if messages.from_user is not None:
                                file_name = f"downloads/{messages.from_user.username}/{message_id}_{file_name}"
                            else:
                                file_name = f"downloads/{chat_id}/{message_id}_{file_name}"
                            
                            
                            async def progress(current, total):
                                if total != 0:
                                    print(f"{current * 100 / total:.1f}%")
                                else:
                                    print(
                                        f"[*] Download of {file_name.split('/')[-1]} is complete!"
                                    )

                            await app.download_media(
                                file_id,
                                file_name=file_name,
                                progress=progress,
                            )
                        
                        if messages.from_user is not None:
                            username = messages.from_user.username
                            directory = f'Downloads/{username}/logs'
                            if not os.path.exists(directory):
                                os.makedirs(directory)
                            with open(f'{directory}/{username}_bot.txt', 'a') as file:
                                file.write(f"Message ID: {messages.id}\n")
                                file.write(
                                    f"From User ID: {messages.from_user.id} - Username: {messages.from_user.username}\n"
                                )
                                file.write(f"Date: {messages.date}\n")
                                file.write(f"Text: {messages.text}\n")
                                file.write(f"Reply_markup: {messages.reply_markup}\n\n")
                            
                            with open(f'{directory}/{username}_bot.json',
                                      'a') as file:
                                file.write(str(messages))
                        else:
                            directory = f'Downloads/{chat_id}/logs'
                            with open(f'{directory}/{chat_id}_bot.txt', 'a') as file:
                                file.write(f"Message ID: {messages.id}\n")
                                file.write(f"Date: {messages.date}\n")
                                file.write(f"Text: {messages.text}\n")
                                file.write(f"Reply_markup: {messages.reply_markup}\n\n")
                            
                            with open(f'{directory}/{chat_id}_bot.json', 'a') as file:
                                file.write(str(messages))
        except AttributeError as e:
            print(f"Error: {e}")
            pass
        except Exception as e:
            print(f"Error: {e}")
            pass

    
    
    original_input = input
    def patched_input(prompt_text):
        if "Enter phone number or bot token:" in prompt_text:
            print(f"[*] Automatically using bot token: {bot_token}")
            return bot_token
        elif prompt_text.lower().endswith("(y/n)") or prompt_text.lower().endswith("(y/n):"):
            print("[*] Automatically confirming with 'y'")
            return "y"
        
        return original_input(prompt_text)
    
    
    __builtins__["input"] = patched_input
    
    try:
        app.run(main(num_messages, message_id))
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        
        __builtins__["input"] = original_input
        app.disconnect()
        pass
