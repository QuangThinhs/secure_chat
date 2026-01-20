import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from services import api_client

class InfoPanel(QWidget):
    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app
        self.current_user_id = None
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_path = os.path.join(current_dir, "assets")
        self.init_ui()

    def get_icon(self, name):
        path = os.path.join(self.assets_path, name)
        if os.path.exists(path): return QIcon(path)
        return QIcon()

    def init_ui(self):
        self.setFixedWidth(340)
        self.setStyleSheet("""
            QWidget {
                background-color: #F7F9FA;
                border-left: 1px solid #CFD8DC;
                font-family: 'Segoe UI', sans-serif;
                font-size: 18px; /* Font to */
            }
            QFrame#header {
                background-color: #FFFFFF;
                border-bottom: 1px solid #CFD8DC;
            }
            QLabel#header_title { font-weight: bold; font-size: 18px; color: #263238; }
            QLabel#full_name { font-weight: bold; font-size: 24px; margin-top: 20px; color: #1E88E5; }
            QLabel#username { color: #546E7A; margin-bottom: 25px; font-size: 16px; }
            QPushButton#close_btn { background: transparent; border: none; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(80)
        h_layout = QHBoxLayout(header)
        
        self.header_title = QLabel("Thông tin liên hệ")
        self.header_title.setObjectName("header_title")
        
        self.close_btn = QPushButton()
        self.close_btn.setObjectName("close_btn")
        self.close_btn.setIcon(self.get_icon("close.png"))
        self.close_btn.setCursor(Qt.PointingHandCursor)
        
        h_layout.addWidget(self.header_title)
        h_layout.addStretch()
        h_layout.addWidget(self.close_btn)
        main_layout.addWidget(header)

        # Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        
        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setAlignment(Qt.AlignTop)
        c_layout.setContentsMargins(30, 30, 30, 30)
        
        self.avatar_label = QLabel()
        self.avatar_label.setAlignment(Qt.AlignCenter)
        pix = self.get_icon("user.png").pixmap(100, 100)
        self.avatar_label.setPixmap(pix)
        
        self.full_name_label = QLabel("Đang tải...")
        self.full_name_label.setObjectName("full_name")
        self.full_name_label.setAlignment(Qt.AlignCenter)
        
        self.username_label = QLabel("@...")
        self.username_label.setObjectName("username")
        self.username_label.setAlignment(Qt.AlignCenter)
        
        lbl_bio = QLabel("Giới thiệu:")
        lbl_bio.setStyleSheet("font-weight: bold; margin-top: 15px;")
        
        self.bio_label = QLabel("")
        self.bio_label.setWordWrap(True)
        self.bio_label.setStyleSheet("color: #37474F; background: white; padding: 15px; border-radius: 10px;")
        
        c_layout.addWidget(self.avatar_label)
        c_layout.addWidget(self.full_name_label)
        c_layout.addWidget(self.username_label)
        c_layout.addWidget(lbl_bio)
        c_layout.addWidget(self.bio_label)
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def load_user_info(self, user_id):
        if not user_id: return
        self.current_user_id = user_id
        token = self.parent_app.token
        status, data = api_client.get_user_info(token, user_id)
        if status == 200:
            self.full_name_label.setText(data.get("full_name", "Không có tên"))
            self.username_label.setText(f"@{data.get('username')}")
            self.bio_label.setText(data.get("bio", "Chưa có giới thiệu."))
        else:
            self.full_name_label.setText("Lỗi")
            self.bio_label.setText("Không thể tải thông tin.")