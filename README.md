# MikShaf - Telegram OSINT TOOL 

MikShaf is a the most powerful command-line tool for managing, downloading, and analyzing Telegram chat data. It provides a comprehensive set of features for both bot and user sessions, allowing you to efficiently monitor, download, and process Telegram messages.

## ⚠️ DISCLAIMER ⚠️

**USE AT YOUR OWN RESPONSIBILITY**

This tool is provided for educational and legitimate data management purposes only. I AM NOT responsible for any misuse of this software. By using this tool, you agree to:

1. Comply with Telegram's Terms of Service
2. Only access data for which you have proper authorization
3. Respect privacy and data protection laws in your jurisdiction
4. Not use this tool for spamming, harassment, or any malicious activities

Again pls use it responsibly and ethically.

## Features

- **Session Management**: Create and manage multiple bot and user sessions
- **Message Downloading**: Download and archive message history from Telegram chats
- **Detailed Chat Info**: Get comprehensive information about Telegram chats
- **Message Monitoring**: Real-time monitoring of incoming messages
- **Message Management**: Send, delete, and forward messages programmatically
- **Background Processing**: Efficient background processing of download tasks

## Requirements

- Python 3.7 or higher
- Required Python packages (see requirements.txt)
- Telegram API credentials (API_ID and API_HASH) in .env file, you can get these free at : https://my.telegram.org/

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/4ng3If/telegram-dumper-MikShaf.git
   cd telegram-dumper-MikShaf
   ```

2. Create and activate a virtual environment (for newbies):
   ```
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run the main script:
   ```
   python main.py
   ```

## First Run Configuration

Dont forget this : Telegram API_ID and API_HASH (obtain from https://my.telegram.org/apps)

## Basic Usage

### Main Menu Options

- **1. Add Target**: Add a new bot session to monitor
- **2. Saved Session**: View and select from saved sessions
- **3. Detailed Chat Info**: Get detailed information about a chat
- **I. Comprehensive Bot Info**: Get comprehensive information about a bot
- **M. Monitor Messages**: Monitor incoming messages in real-time
- **A. Start Auto-Update**: Enable automatic checking for new messages
- **S. Stop Auto-Update**: Disable automatic message checking
- **U. Auto-Update Status**: View status of auto-update processes
- **4. Send Message**: Send a message to a Telegram chat
- **5. Spam Chat**: Send multiple messages to a chat (use responsibly)
- **6. Delete Recent Messages**: Delete recent messages from a chat
- **7. Download All Messages**: Download all messages from a chat
- **8. Forward Messages**: Forward messages between chats
- **9. Send File**: Send a file to a Telegram chat
- **C. Clear Current Session**: Clear the current active session
- **0. Exit**: Exit the application

## Project Structure

- **handlers/**: Command handlers for different functionalities
- **utils/**: Utility functions for UI, Telegram operations, etc.
- **telegram_data/**: Storage for session data
  - **bot_sessions/**: Bot session files
  - **user_sessions/**: User session files
- **logs/**: Log files for operations and errors
- **Downloads/**: Downloaded media and message data

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is distributed under the MIT License. See the LICENSE file for more information.

---

Created with ❤️ by 0xtiho
