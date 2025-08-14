"""
Cấu hình dùng chung cho cả Server và Client
Tách riêng HOST cho server bind và client connect để dễ thay đổi khi triển khai
"""
HOST_SERVER_BIND = "0.0.0.0"  # Lắng nghe trên tất cả IP của máy chủ
HOST_CLIENT_CONNECT = "127.0.0.1"
PORT_CHAT = 5001
PORT_AUDIO = 5002
BUFFER_SIZE = 1024  
ENCODING = "utf-8"  