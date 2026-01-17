```plaintext
Cấu Trúc Thư Mục Dự Tính
secure_chat/
│
├── app.py                 # Tạo Flask app (factory) + khởi tạo extensions
├── config.py              # Cấu hình (DB, JWT, socket...)
│
├── models/                # ORM models (SQLAlchemy)
│   ├── __init__.py
│   ├── user.py....
│
├── routes/                # Các route 
│   ├── account.py         # Đăng ký / đăng nhập / đăng xuất
│   ├── users.py....       # Lấy thông tin user, cập nhật profile
│
├── services/              # Các service phía client
│   ├── __init__.py
│   ├── api_client.py....  # Gọi REST API tới backend
│
├── UI/                    # Giao diện PyQt5
│   ├── __init__.py
│   ├── main.py....        # Điểm vào cho client GUI (chạy bằng python -m UI.main)
│
└── run.py                 # File khởi chạy Flask app 