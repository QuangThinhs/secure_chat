import os
import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap, QIcon
from services import api_client, crypto_client 

class LoginPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.password_visible = False
        
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
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #E3F2FD, stop:1 #BBDEFB);
                font-family: 'Segoe UI', sans-serif;
                font-size: 18px; /* Font to */
            }
            QFrame#container {
                background-color: #FFFFFF;
                border-radius: 24px;
                border: 1px solid #FFFFFF;
            }
            QLabel { background: transparent; color: #37474F; }
            QLabel#title {
                color: #1565C0;
                font-size: 40px; /* Tiêu đề rất to */
                font-weight: bold;
            }
            QLabel#subtitle {
                color: #78909C;
                font-size: 20px;
            }
            QLineEdit {
                background-color: #F5F7FA;
                border: 1px solid #CFD8DC;
                border-radius: 12px;
                padding: 14px 14px 14px 45px; 
                font-size: 18px; 
                color: #263238;
            }
            QLineEdit:focus {
                border: 2px solid #1E88E5;
                background-color: #FFFFFF;
            }
            QPushButton#primary {
                background-color: #1E88E5;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 18px;
                padding: 16px;
            }
            QPushButton#primary:hover { background-color: #1976D2; }
            QPushButton#secondary {
                background-color: white;
                color: #546E7A;
                border: 1px solid #CFD8DC;
                border-radius: 12px;
                font-weight: 600;
                font-size: 16px;
                padding: 14px;
            }
            QPushButton#secondary:hover { background-color: #ECEFF1; color: #37474F; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        container = QFrame()
        container.setObjectName("container")
        container.setFixedWidth(500) # Card to hơn

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 10)
        container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(container)
        layout.setSpacing(30)
        layout.setContentsMargins(60, 60, 60, 60)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(15)
        
        logo_label = QLabel()
        logo_pix = QPixmap(os.path.join(self.assets_path, "logo.png"))
        if not logo_pix.isNull():
            logo_label.setPixmap(logo_pix.scaled(110, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            logo_label.setText("💠")
            logo_label.setStyleSheet("font-size: 90px;")
        logo_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(logo_label)

        title = QLabel("Secure Chat")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)

        subtitle = QLabel("Đăng nhập để kết nối")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle)

        layout.addLayout(header_layout)

        # Inputs
        form_layout = QVBoxLayout()
        form_layout.setSpacing(25)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Tên đăng nhập")
        self.username_input.setMinimumHeight(55)
        self.username_input.addAction(self.get_icon("user.png"), QLineEdit.LeadingPosition)
        form_layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mật khẩu")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(55)
        self.password_input.addAction(self.get_icon("lock.png"), QLineEdit.LeadingPosition)
        
        self.toggle_action = self.password_input.addAction(self.get_icon("eye_close.png"), QLineEdit.TrailingPosition)
        self.toggle_action.triggered.connect(self.toggle_password_visibility)

        form_layout.addWidget(self.password_input)
        layout.addLayout(form_layout)

        # Buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(15)
        layout.addSpacing(15)

        self.login_btn = QPushButton("ĐĂNG NHẬP")
        self.login_btn.setObjectName("primary")
        self.login_btn.setCursor(Qt.PointingHandCursor)

        self.register_btn = QPushButton("Tạo tài khoản mới")
        self.register_btn.setObjectName("secondary")
        self.register_btn.setCursor(Qt.PointingHandCursor)

        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.register_btn)
        layout.addLayout(btn_layout)

        self.message_label = QLabel("")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("color: #D32F2F; font-size: 16px; margin-top: 15px; font-weight: bold;")
        layout.addWidget(self.message_label)

        main_layout.addWidget(container)

        self.login_btn.clicked.connect(self.do_login)
        self.register_btn.clicked.connect(self.go_to_register)
        self.username_input.returnPressed.connect(self.do_login)
        self.password_input.returnPressed.connect(self.do_login)

    def go_to_register(self):
        self.parent.layout.setCurrentWidget(self.parent.register_page)

    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_action.setIcon(self.get_icon("eye_open.png"))
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_action.setIcon(self.get_icon("eye_close.png"))

    def show_message(self, message, error=True):
        color = "#D32F2F" if error else "#1E88E5"
        self.message_label.setStyleSheet(f"color: {color}; font-size: 16px; margin-top: 15px; font-weight: 600;")
        self.message_label.setText(message)

    def do_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            self.show_message("Vui lòng nhập đầy đủ thông tin.", error=True)
            return

        self.login_btn.setEnabled(False)
        self.register_btn.setEnabled(False)
        self.show_message("Đang xác thực...", error=False)
        self.login_btn.setText("Đang tải...")

        def login_thread():
            token, user_id, status, data = api_client.login(username, password)
            if status == 200:
                try:
                    private_key = crypto_client.load_private_key(username, password)
                except Exception as e:
                    self.show_message(f"Lỗi khóa bảo mật: {str(e)}", error=True)
                    self.reset_ui()
                    return

                self.parent.token = token
                self.parent.user_id = user_id
                self.parent.private_key = private_key
                
                self.username_input.clear()
                self.password_input.clear()
                self.show_message("", error=False)

                self.parent.home_page.connect_socket()
                self.parent.home_page.refresh_chats()
                self.parent.home_page.set_current_user_label()
                self.parent.layout.setCurrentWidget(self.parent.home_page)
            else:
                error_msg = data.get("msg", "Đăng nhập thất bại")
                self.show_message(f"Lỗi: {error_msg}", error=True)
            
            self.reset_ui()

        threading.Thread(target=login_thread, daemon=True).start()

    def reset_ui(self):
        self.login_btn.setEnabled(True)
        self.register_btn.setEnabled(True)
        self.login_btn.setText("ĐĂNG NHẬP")