# Multi-Client - Guessing Number Game - Midterm Project

## Mô tả dự án
Đây là đồ án giữa kì môn ** Lập trình mạng ** , được thực hiện bởi ** Nhóm 12 ** ứng dụng là một trò chơi đơn giản, cho phép nhiều Người chơi(Client) kết nối đến máy chủ(Server) thông qua socket TCP và tham gia trò chơi "Đoán số" độc lập

## Thành viên nhóm
- ** Nguyễn Tấn Tài**  Client và tổng hợp báo cáo
- ** Trương Hoàng Tuấn Kiệt**  Server
- ** Nguyễn Trung Kiên**Client GUI(Tkinter)

## Mô hình kiến trúc
Ứng dụng được xây dựng theo mô hình **Client-Server đa kết nối( Multi Client TCP socket)**:
- 'Server.py' : Lắng nghe nhiều Client, xử lý trò chơi của từng người độc lập.
- 'Client.py' :  Giao diện terminal đơn giản.
- 'ClientGUI.py' : Giao diện người dùng bằng tkinter với giao diện đồ họa thân thiện.

Mỗi Client có thể :
- Nhập tên người chơi.
- Đoán số trong khoảng 1-100.
- Nhập phản hồi từ Server(thấp hơn, cao hơn, đúng) .
- Hiển thị số lần đoán còn lại.

## Chức năng chính
- Giao tiếp mạng qua TCP socket.
- Hỗ trợ nhiều Client đồng thời.
- Reset trò chơi sau mỗi lượt chơi.
- Giao diện đẹp, có hình nền.
- Server có chức năng lưu tên người dùng đăng nhập, lưu lại ip Client khi kết nối vào Server.

## Cấu trúc thư mục
├── Client.py # Giao diện dòng lệnh
├── ClientGUI.py # Giao diện đồ họa (Tkinter)
├── README.md # Tài liệu hướng dẫn (file này)
├── Background.jpg # Hình nền GUI
├── server.py # Server chính lắng nghe kết nối
 
## Hướng dẫn chạy chương trình
 ### 1 Cài đặt
 Cần python 3.10+ và các thư viện :
 ''Bash
    pip install pillow
 ### 2 Chạy Server( trên 1 máy)
    python server.py
 ### 3 Chạy Client( trên máy khác hoặc máy chủ)
    python Client.py
 ### 3 Chạy ClientGUI
    python ClientGUI.py
