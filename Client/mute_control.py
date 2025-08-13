# mute_control.py
class MuteControl:
    def __init__(self, client):
        self.is_muted = False
        
    def mute(self):
        """Tắt micro"""
        self.is_muted = True
        print("[MuteControl] Micro đã tắt.")
        
    def unmute(self):
        """Bật micro"""
        self.is_muted = False   
        print("[MuteControl] Micro đã bật.")
        
    def toggle_(self):
        """Chuyển đổi trạng thái micro"""
        self.is_muted = not self.is_muted
        print(f"[MuteControl] Micro đang {'tắt'if self.is_muted else'bật'}.")
    def get_status(self):
        """Lấy trạng thái micro"""
        return self.is_muted