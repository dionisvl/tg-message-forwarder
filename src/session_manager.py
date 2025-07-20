import os

class SessionManager:
    @staticmethod
    def load_session(session_type='user'):
        if not os.path.exists('sessions'):
            os.makedirs('sessions')
        
        file_path = f'sessions/session{"_bot" if session_type == "bot" else ""}.txt'
        try:
            with open(file_path, 'r') as f:
                return f.read().strip() or None
        except FileNotFoundError:
            return None
    
    @staticmethod
    def save_session(session_str, session_type='user'):
        if not os.path.exists('sessions'):
            os.makedirs('sessions')
        
        file_path = f'sessions/session{"_bot" if session_type == "bot" else ""}.txt'
        try:
            with open(file_path, 'w') as f:
                f.write(session_str)
            return True
        except:
            return False