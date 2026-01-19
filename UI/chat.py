# UI/chat.py
import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
    QLabel, QFrame, QScrollBar
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QTextBlockFormat, QTextCursor, QTextCharFormat

from services import api_client, crypto_client

class ChatPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent # HomePage
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_path = os.path.join(current_dir, "assets")
        self.init_ui()

    def get_icon(self, name):
        path = os.path.join(self.assets_path, name)
        if os.path.exists(path): return QIcon(path)
        return QIcon()

    def init_ui(self):
        # --- CSS FONT 18px ---
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                font-family: 'Segoe UI', sans-serif;
                font-size: 18px; /* Font to */
            }
            QFrame#header {
                background-color: #FFFFFF;
                border-bottom: 1px solid #CFD8DC;
            }
            QLabel#title {
                color: #263238; font-size: 20px; font-weight: bold;
            }
            QLabel#status {
                color: #1E88E5; font-size: 16px;
            }
            QPushButton.action_btn {
                background-color: transparent; border: none; border-radius: 8px; padding: 6px;
            }
            QPushButton.action_btn:hover { background-color: #F0F4F8; }
            
            QTextEdit#messages {
                border: none; background-color: #FFFFFF; padding: 25px;
                font-size: 18px; /* Tin nhắn to */
                color: #37474F;
            }
            
            QFrame#input_frame {
                background-color: #F0F4F8; border-top: 1px solid #CFD8DC; padding: 15px 30px;
            }
            QFrame#input_bg {
                background-color: #FFFFFF; border: 1px solid #B0BEC5; border-radius: 26px;
            }
            QFrame#input_bg:focus-within { border: 1px solid #1E88E5; }
            QLineEdit#input {
                border: none; background: transparent; padding: 14px; font-size: 18px;
            }
            QPushButton#send_btn, QPushButton#attach_btn {
                background: transparent; border: none; border-radius: 20px; padding: 10px;
            }
            QPushButton#send_btn:hover, QPushButton#attach_btn:hover { background-color: #ECEFF1; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header_frame = QFrame()
        header_frame.setObjectName("header")
        header_frame.setFixedHeight(80)
        header = QHBoxLayout(header_frame)
        header.setContentsMargins(30, 0, 30, 0)
        
        self.avatar_label = QLabel()
        self.avatar_label.setPixmap(self.get_icon("user.png").pixmap(45, 45))
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        title_layout.setAlignment(Qt.AlignVCenter)
        
        self.title_label = QLabel("Cuộc hội thoại")
        self.title_label.setObjectName("title")
        self.status_label = QLabel("Ngoại tuyến")
        self.status_label.setObjectName("status")
        
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.status_label)
        
        self.call_button = QPushButton()
        self.call_button.setIcon(self.get_icon("call.png"))
        self.call_button.setIconSize(QSize(28, 28))
        self.call_button.setProperty("class", "action_btn")
        self.call_button.setCursor(Qt.PointingHandCursor)
        self.call_button.setToolTip("Gọi thoại")
        
        self.video_button = QPushButton()
        self.video_button.setIcon(self.get_icon("video.png"))
        self.video_button.setIconSize(QSize(28, 28))
        self.video_button.setProperty("class", "action_btn")
        self.video_button.setCursor(Qt.PointingHandCursor)
        self.video_button.setToolTip("Gọi video")
        
        self.info_button = QPushButton()
        self.info_button.setIcon(self.get_icon("info.png"))
        self.info_button.setIconSize(QSize(28, 28))
        self.info_button.setProperty("class", "action_btn")
        self.info_button.setCursor(Qt.PointingHandCursor)
        self.info_button.setToolTip("Thông tin")

        header.addWidget(self.avatar_label)
        header.addLayout(title_layout)
        header.addStretch()
        header.addWidget(self.call_button)
        header.addWidget(self.video_button)
        header.addWidget(self.info_button)
        main_layout.addWidget(header_frame)

        # Message Area
        self.messages = QTextEdit()
        self.messages.setObjectName("messages")
        self.messages.setReadOnly(True)
        main_layout.addWidget(self.messages, 1)

        # Input Area
        input_container = QFrame()
        input_container.setObjectName("input_frame")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        input_bg = QFrame() 
        input_bg.setObjectName("input_bg")
        input_bg_layout = QHBoxLayout(input_bg)
        input_bg_layout.setContentsMargins(5, 5, 5, 5)
        
        self.attach_btn = QPushButton()
        self.attach_btn.setObjectName("attach_btn")
        self.attach_btn.setIcon(self.get_icon("attach.png"))
        self.attach_btn.setCursor(Qt.PointingHandCursor)
        self.attach_btn.setToolTip("Đính kèm file")
        
        self.input = QLineEdit()
        self.input.setObjectName("input")
        self.input.setPlaceholderText("Nhập tin nhắn...")
        
        self.send_btn = QPushButton()
        self.send_btn.setObjectName("send_btn")
        self.send_btn.setIcon(self.get_icon("send.png"))
        self.send_btn.setIconSize(QSize(26, 26))
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.setToolTip("Gửi")
        
        input_bg_layout.addWidget(self.attach_btn)
        input_bg_layout.addWidget(self.input, 1)
        input_bg_layout.addWidget(self.send_btn)
        
        input_layout.addWidget(input_bg)
        main_layout.addWidget(input_container)

        self.send_btn.clicked.connect(self.send)
        self.input.returnPressed.connect(self.send)

    def clear_chat(self):
        self.messages.clear()
        self.input.clear()
        self.title_label.setText("Chat")
        self.status_label.setText("...")

    def load_chat(self, chat_id):
        from .home import sio 
        
        token = self.parent.parent.token
        user_id = self.parent.parent.user_id
        private_key = self.parent.parent.private_key
        
        if not sio.connected: 
            try: self.parent.connect_socket() 
            except: pass
        else:
            sio.emit("join_chat", {"chat_id": chat_id, "user_id": user_id})

        status, chat = api_client.get_chat_detail(token, chat_id)
        if status == 200:
            self.title_label.setText(chat.get('name', 'Hội thoại'))
            if not chat.get('is_group'):
                members = chat.get('members', [])
                other_id = next((m for m in members if m != user_id), None)
                self.parent.current_other_user_id = other_id 
            else:
                self.parent.current_other_user_id = None

        status, msgs = api_client.get_messages(token, chat_id)
        self.messages.clear()
        if status == 200:
            for msg in msgs:
                is_me = msg['sender_id'] == user_id
                try:
                    key_dict = json.loads(msg['aes_key_encrypted'])
                    wrapped = key_dict.get(str(user_id))
                    if wrapped:
                        aes_key = crypto_client.unwrap_aes_key(wrapped, private_key)
                        text = crypto_client.decrypt_aes_gcm(msg['content'], aes_key, msg['iv'], msg['tag'])
                    else: text = "[Không có khóa]"
                except Exception as e: text = f"[Lỗi giải mã: {e}]"
                self.add_message(msg['sender_id'], text, is_me)

    def send(self):
        from .home import sio 
        text = self.input.text().strip()
        if not text: return

        token = self.parent.parent.token
        user_id = self.parent.parent.user_id
        chat_id = self.parent.current_chat_id
        
        if not chat_id: return
        
        status, chat = api_client.get_chat_detail(token, chat_id)
        if status != 200: return
        
        aes_key = crypto_client.generate_aes_key()
        enc = crypto_client.encrypt_aes_gcm(text, aes_key)
        wrapped_keys = {}
        for mid in chat["members"]:
            s, info = api_client.get_user_info(token, mid)
            if s == 200:
                wrapped = crypto_client.wrap_aes_key(aes_key, info["public_key"])
                wrapped_keys[str(mid)] = wrapped
        
        payload = {
            "chat_id": chat_id, "sender_id": user_id,
            "content": enc["ciphertext"], "aes_key_encrypted": wrapped_keys,
            "iv": enc["iv"], "tag": enc["tag"]
        }
        try:
            sio.emit("send_message", payload)
            self.input.clear()
        except Exception as e: print(e)

    def add_message(self, sender_id, text, is_me):
        """
        SỬA LỖI CĂN LỀ: Dùng QTextCursor và QTextBlockFormat để ép buộc căn lề.
        """
        text = text.replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
        
        # 1. Lấy con trỏ văn bản hiện tại
        cursor = self.messages.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # 2. Tạo định dạng Block (đoạn văn)
        block_format = QTextBlockFormat()
        if sender_id == "System":
            block_format.setAlignment(Qt.AlignCenter)
            block_format.setTopMargin(10)
            block_format.setBottomMargin(10)
        elif is_me:
            block_format.setAlignment(Qt.AlignRight) # Căn phải tuyệt đối
            block_format.setTopMargin(5)
            block_format.setBottomMargin(5)
            block_format.setLeftMargin(50) # Thụt lề để không quá dài
        else:
            block_format.setAlignment(Qt.AlignLeft) # Căn trái tuyệt đối
            block_format.setTopMargin(5)
            block_format.setBottomMargin(5)
            block_format.setRightMargin(50)

        # 3. Chèn Block mới với định dạng trên
        cursor.insertBlock(block_format)

        # 4. Chèn nội dung HTML (Chỉ chứa màu sắc và font, không chứa thẻ div align)
        if sender_id == "System":
            html = f"<span style='color: #90A4AE; font-size: 14px;'>{text}</span>"
        elif is_me:
            # CHỮ MÀU XANH, ĐẬM, KHÔNG NỀN
            html = f"<span style='color: #1565C0; font-weight: bold; font-size: 18px;'>{text}</span>"
        else:
            # CHỮ MÀU ĐEN/XÁM, KHÔNG NỀN
            html = f"<span style='color: #37474F; font-size: 18px;'>{text}</span>"
            
        cursor.insertHtml(html)
        
        # 5. Cuộn xuống dưới cùng
        self.messages.setTextCursor(cursor)
        self.messages.verticalScrollBar().setValue(self.messages.verticalScrollBar().maximum())