# SecureChat — Encrypted Messenger (Flask + PyQt5)

Ứng dụng nhắn tin **mã hóa đầu-cuối (E2EE)** 

* Backend: Flask + SocketIO + SQLAlchemy
* Frontend: PyQt5 (Dark UI)
* Crypto: RSA + AES-GCM

## Chạy Dự Án (Chạy Nhiều Phiên Đồng Thời)

> **Lưu ý:** Dự án bao gồm server HTTP (Flask), socket server (SocketIO) và nhiều client PyQt5.

1. **Khởi động Flask App + REST API:**
  - **Cài đặt môi trường:**
    1. Tạo môi trường ảo:

      ```bash
      python -m venv venv
      ```

    2. Cài đặt các thư viện cần thiết:

      ```bash
      pip install -r requirements.txt
      ```

    3. Chạy server Flask:

      ```bash
      python run.py
      ```

2. **Khởi động Socket Server:**

  ```bash
  python -m services.socket_client
  ```

  Socket server này sẽ lắng nghe trên port mặc định `5001` và sử dụng `async_mode='threading'`.

3. **Chạy Nhiều Client PyQt5 Để Giả Lập Nhiều User:**
  - Mở hai cửa sổ terminal khác nhau:

  ```bash
  python -m UI.main   # client user1
  python -m UI.main   # client user2
  ```

  - Hoặc trên Windows PowerShell:

  ```powershell
  py -3 -m UI.main   # user1
  py -3 -m UI.main   # user2
  ```

---

## Sơ đồ thư mục (phiên bản cập nhật)

```
secure_chat/
│
├── app.py                 # Tạo Flask app (factory) + khởi tạo extensions
├── config.py              # Cấu hình (DB, JWT, socket...)
│
├── models/                # ORM models (SQLAlchemy)
│   ├── __init__.py
│   ├── user.py
│   ├── message.py
│   ├── chat.py
│   └── __all_models__.py
│
├── routes/                # Các route Flask Blueprint
│   ├── __init__.py  
│   ├── account.py         # Đăng ký / đăng nhập / đăng xuất
│   ├── users.py           # Lấy thông tin user, cập nhật profile
│   ├── chats.py           # Tạo/lấy thông tin chat, thành viên
│   ├── messages.py        # REST API cho tin nhắn
│   └── status.py          # API trạng thái online/offline
│
├── services/              # Các service phía client
│   ├── __init__.py
│   ├── api_client.py      # Gọi REST API tới backend
│   ├── crypto_client.py   # Xử lý mã hóa AES / RSA
│   └── socket_client.py   # Server socket độc lập (chạy bằng python -m services.socket_client)
│
├── UI/                    # Giao diện PyQt5
│   ├── __init__.py
│   ├── main.py            # Điểm vào cho client GUI (chạy bằng python -m UI.main)
│   ├── login.py           # Giao diện đăng nhập/đăng ký
│   ├── home.py            # Danh sách chat + người dùng online
│   └── chat.py            # Cửa sổ chat đơn (kiểu Telegram)
│
├── requirements.txt
└── run.py                 # File khởi chạy Flask app (py run.py)
```

---

## Ghi chú chi tiết chức năng (note tất cả chức năng)

### 1. Authentication (routes/account.py)

* `POST /auth/register` — Tạo tài khoản mới.

  * Yêu cầu: `username`, `password`, `public_key`.
  * Phục vụ: lưu account, public key; trả về `user_id`.
* `POST /auth/login` — Đăng nhập.

  * Trả về JWT token và `user_id`.
* `POST /auth/logout` (JWT protected) — Đặt status offline.

### 2. Users (routes/users.py)

* `GET /users/<id>` — Lấy thông tin người dùng, gồm `public_key`, `status`, `last_seen`, profile.
* `PUT /users/me` — Cập nhật profile bản thân.

### 3. Chats (routes/chats.py)

* `POST /chats` — Tạo chat (1-1 hoặc group). 1-1 yêu cầu 1 member (ngoài creator).
* `GET /chats` — Lấy danh sách chat hiện có của người dùng.
* `GET /chats/<id>` — Chi tiết chat (kiểm tra quyền truy cập thành viên).

### 4. Messages (routes/messages.py)

* `GET /chats/<chat_id>/messages` — Lấy lịch sử tin nhắn (sắp xếp theo timestamp asc).
* `POST /chats/<chat_id>/messages` — Gửi tin nhắn (REST fallback).

  * Payload chứa: `content`, `aes_key_encrypted` (JSON/dict or stringified), `iv`, `tag`.
  * Server lưu tin, tạo MessageRecipient cho mọi thành viên.

### 5. Status (routes/status.py)

* `POST /status` — Cập nhật `online` / `offline` cho user (JWT protected).
* `GET /status/<user_id>` — Lấy trạng thái & last_seen.

### 6. Socket server (services/socket_client.py)

* Event `connect` — Xác thực token, lưu mapping `user_id -> sid`, broadcast `online_users`.
* Event `join_chat` — `join_room('chat_<id>')`.
* Event `send_message` — Lưu message vào DB (aes_key_encrypted lưu dạng JSON string), tạo recipients và emit `receive_message` tới room `chat_<id>` (include_self=True).
* Event `disconnect` — Xoá mapping, broadcast lại `online_users`.

### 7. Client services (services/api_client.py & services/crypto_client.py)

* `api_client` cung cấp wrapper debug logging cho tất cả REST call (login, get_chats, get_messages, ...).
* `crypto_client` cung cấp: generate_rsa_keypair, generate_aes_key, encrypt/decrypt AES-GCM, wrap/unwrap AES bằng RSA, save/load private key (file encrypted with passphrase PBKDF2+AES-GCM).

### 8. UI (UI/main.py, login.py, home.py, chat.py)

* `main.py` tạo `ChatApp` (QStackedLayout) gồm `LoginPage`, `HomePage`, `ChatPage`.
* `LoginPage` — Đăng ký / đăng nhập, lưu private key (local file `keys/{username}_private.enc.json`).
* `HomePage` — Danh sách chat, online users; xử lý socket connect và sự kiện "receive_message" để cập nhật UI realtime.
* `ChatPage` — Hiển thị message bubble (Telegram-like), gửi tin qua socket (`send_message`) hoặc REST fallback.

---

## Debug & Lưu ý vận hành

* Nếu client không thấy tin nhắn realtime: kiểm tra `services.socket_client` có chạy, và client `sio.connect(...)` có token hợp lệ.
* Socket server thường chạy trên port `5001` (cấu hình trong `services/socket_client.py` và client `UI/home.py`).
* Khi `socketio.emit('receive_message', ..., include_self=True)` — server gửi lại cả cho sender. Tránh hiện tin lặp: client **không** nên append tin gửi 2 lần (nếu client đã append khi gửi, server include_self=True sẽ khiến lặp).

  * Cách xử lý: chọn 1 trong 2 chiến lược

    1. **Client không append khi gửi** — đợi event `receive_message` từ server để append (recommended).
    2. **Client append ngay khi gửi** — server emit `receive_message` với `include_self=False` (hoặc client ignore message có `sender_id == my_id` và `id` trùng với tin đã append).

Mục tiêu của repo hiện tại: giữ server emit `include_self=True` (để nhất quán), do đó **client UI nên *không* tự append duplicate**. Hãy để `add_message()` chỉ do khi nhận event `receive_message` hoặc sau load messages.

---
