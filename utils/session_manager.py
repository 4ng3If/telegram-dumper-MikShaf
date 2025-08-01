import os
import json
import datetime
import re
from utils.telegram_utils import parse_bot_token
from utils.ui_utils import color, warning, info, success, error, YLW, CYN, GRN, RED, MGA

class SessionManager:
    def __init__(self, session_dir):
        self.SESSION_DIR = session_dir
        if not os.path.exists(self.SESSION_DIR):
            os.makedirs(self.SESSION_DIR)

    def get_session_filepath(self, bot_token, from_chat_id, session_name=None):
        """Returns the session file path for a specific bot session."""
        bot_token = parse_bot_token(bot_token)
        if session_name:
            
            safe_name = re.sub(r'[^\w\s-]', '', session_name).strip().replace(' ', '_')
            return os.path.join(self.SESSION_DIR, f"{safe_name}.json")
        
        return os.path.join(self.SESSION_DIR, f"{bot_token.replace(':', '+')}_{from_chat_id}.json")

    def load_sessions(self):
        """Loads all available session files from the 'sessions' directory."""
        sessions = {}
        for filename in os.listdir(self.SESSION_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(self.SESSION_DIR, filename)
                try:
                    with open(filepath, "r") as f:
                        session_data = json.load(f)
                        sessions[filename] = session_data
                except json.JSONDecodeError:
                    print(f"{warning} Invalid JSON in {filename}, skipping")
                except Exception as e:
                    print(f"{error} Error loading {filename}: {e}")
        return sessions

    def load_single_session(self, bot_token, from_chat_id, session_name=None):
        """Loads a single session file."""
        
        if session_name:
            
            sessions = self.load_sessions()
            for session in sessions.values():
                if session.get("session_name") == session_name:
                    return session
        
        
        filepath = self.get_session_filepath(bot_token, from_chat_id, session_name)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"{error} Error loading session: {e}")
                return None
                
        
        sessions = self.load_sessions()
        for session in sessions.values():
            if session.get("bot_token") == bot_token and str(session.get("from_chat_id")) == str(from_chat_id):
                return session
                
        return None  

    def save_sessions(self, bot_token, from_chat_id, session_data):
        """Saves the session data to its corresponding file."""
        session_name = session_data.get("session_name", None)
        filepath = self.get_session_filepath(bot_token, from_chat_id, session_name)
        with open(filepath, "w") as f:
            json.dump(session_data, f, indent=4)

    def clean_duplicate_sessions(self):
        """Remove duplicate sessions based on bot token and chat ID."""
        try:
            
            sessions = self.load_sessions()
            if not sessions:
                return

            
            grouped_sessions = {}
            for filename, session_data in sessions.items():
                key = f"{session_data.get('bot_token')}_{session_data.get('from_chat_id')}"
                if key not in grouped_sessions:
                    grouped_sessions[key] = []
                grouped_sessions[key].append((filename, session_data))

            
            for key, session_group in grouped_sessions.items():
                if len(session_group) <= 1:
                    continue  
                    
                
                sorted_sessions = sorted(session_group, 
                                        key=lambda x: (x[1].get("is_done", True), 
                                                     -x[1].get("last_message_id", 0)))
                
                
                best_session = sorted_sessions[0]
                
                
                for filename, _ in sorted_sessions[1:]:
                    filepath = os.path.join(self.SESSION_DIR, filename)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        print(f"{info} Removed duplicate session: {filename}")
        except Exception as e:
            print(f"{warning} Error cleaning duplicate sessions: {e}")

    def migrate_sessions(self):
        """Add session_name to existing sessions that don't have it."""
        try:
            sessions = self.load_sessions()
            for filename, session_data in sessions.items():
                if "session_name" not in session_data:
                    
                    bot_name = session_data.get("first_name", "Unknown")
                    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M')
                    session_data["session_name"] = f"{bot_name}_{timestamp}"
                    
                    self.save_sessions(session_data["bot_token"], session_data["from_chat_id"], session_data)
            
            
            self.clean_duplicate_sessions()
        except Exception as e:
            print(f"{warning} Error migrating sessions: {e}")

    def display_session_dashboard(self):
        """Display a dashboard showing the status of all sessions"""
        from utils.ui_utils import generate_box
        
        sessions = self.load_sessions()
        
        if not sessions:
            return  
        
        
        session_list = list(sessions.values())
        
        
        session_list.sort(key=lambda s: (s.get("is_done", False), s.get("session_name", "").lower()))
        
        
        total_sessions = len(session_list)
        active_sessions = sum(1 for s in session_list if not s.get("is_done", False))
        completed_sessions = total_sessions - active_sessions
        total_messages = sum(s.get("last_updated_message_id", 0) for s in session_list)
        downloaded_messages = sum(s.get("last_message_id", 0) for s in session_list)
        
        
        overall_percentage = 0
        if total_messages > 0:
            overall_percentage = min(100, round((downloaded_messages / total_messages) * 100))
        
        
        dashboard_lines = [
            f"{info} {color('Sessions Overview:', MGA)}",
            f"{info} Total Sessions: {color(total_sessions, YLW)}",
            f"{info} Active Sessions: {color(active_sessions, GRN)}",
            f"{info} Completed Sessions: {color(completed_sessions, CYN)}",
            f"{info} Overall Progress: {color(downloaded_messages, YLW)}/{color(total_messages, GRN)} messages ({color(f'{overall_percentage}%', GRN if overall_percentage == 100 else YLW if overall_percentage > 50 else RED)})"
        ]
        
        
        active_list = [s for s in session_list if not s.get("is_done", False)]
        if active_list:
            dashboard_lines.append("")
            dashboard_lines.append(f"{info} {color('Active Session Details:', MGA)}")
            
            for idx, session in enumerate(active_list[:5], start=1):  
                session_name = session.get('session_name', 'Unnamed')
                total = session.get('last_updated_message_id', 0)
                current = session.get('last_message_id', 0)
                percentage = 0
                if total > 0:
                    percentage = min(100, round((current / total) * 100))
                
                progress_color = GRN if percentage == 100 else YLW if percentage > 50 else RED
                dashboard_lines.append(
                    f"{info} {color(session_name, CYN)} - @{session.get('username', 'Unknown')}: "
                    f"{color(current, YLW)}/{color(total, GRN)} ({color(f'{percentage}%', progress_color)})"
                )
            
            
            remaining = len(active_list) - 5
            if remaining > 0:
                dashboard_lines.append(f"{info} +{remaining} more active sessions")
        
        
        print(generate_box(dashboard_lines, -1, title='Sessions Status Dashboard', titleclr=GRN, pos='left'))
