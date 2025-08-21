# history_manager.py
import json
import os
from datetime import datetime

class HistoryManager:
    def __init__(self, file_path="history.json"):
        self.file_path = file_path
        self.history = []
        self.load_history()

    # ---------- QUẢN LÝ LỊCH SỬ ----------
    def add_chat_entry(self, sender, message):
        entry = {
            "type": "CHAT",
            "sender": sender,
            "message": message,
            "timestamp": self._get_current_time()
        }
        self.history.append(entry)
        self.save_history()

    def add_call_entry(self, partner, duration):    
        entry = {
            "type": "CALL",
            "partner": partner,
            "duration": duration,
            "timestamp": self._get_current_time()
        }
        self.history.append(entry)
        self.save_history()

    def get_history(self, filter_type=None):
        if filter_type:
            return [item for item in self.history if item["type"] == filter_type]
        return self.history

    def save_history(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[ERROR] Lưu lịch sử thất bại: {e}")

    def load_history(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except json.JSONDecodeError:
                self.history = []
        else:
            self.history = []

    def _get_current_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
