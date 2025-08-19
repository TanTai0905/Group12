"""
Cấu hình dùng chung cho cả Server và Client
Tách riêng HOST cho server bind và client connect để dễ thay đổi khi triển khai
"""

HOST_SERVER_BIND = "0.0.0.0"  # Lắng nghe trên tất cả IP của máy chủ
HOST_CLIENT_CONNECT = "127.0.0.1"  # IP client kết nối đến

# PORT cho các dịch vụ - mỗi dịch vụ dùng port riêng
PORT_CHAT = 5001      # Chat server
PORT_AUDIO = 5002     # Audio server

# Cấu hình chung
BUFFER_SIZE = 1024
ENCODING = "utf-8"

# Audio config
AUDIO_CHUNK = 1024
AUDIO_RATE = 44100
AUDIO_CHANNELS = 1

# Broadcast settings
BROADCAST_BUFFER_SIZE = 4096  # Kích thước buffer cho broadcast
BROADCAST_INTERVAL = 1.0      # Khoảng thời gian broadcast (giây)
MAX_BROADCAST_CLIENTS = 50    # Số client tối đa trong 1 lần broadcast

# Message headers
HEADER_SYSTEM = b"SYS_MSG|"
HEADER_USER_LIST = b"USER_LIST|"
HEADER_AUDIO = b"AUDIO_DATA|"