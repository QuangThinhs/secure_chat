import os
import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QFrame, QGraphicsDropShadowEffect, QComboBox, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QIcon
from services import crypto_client

class RegisterPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_path = os.path.join(current_dir, "assets")
        self.init_ui()

    def get_icon(self, name):
        path = os.path.join(self.assets_path, name)
        if os.path.exists(path): return QIcon(path)
        return QIcon()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #E3F2FD, stop:1 #BBDEFB);
                font-family: 'Segoe UI', sans-serif;
                font-size: 18px; /* Font to */
            }
            QFrame#container {
                background-color: #FFFFFF;
                border-radius: 20px;
            }
            QLabel#title {
                color: #1565C0; font-size: 38px; font-weight: bold; margin-bottom: 15px;
            }
            QLineEdit, QComboBox, QDateEdit {
                background-color: #F5F7FA;
                border: 1px solid #CFD8DC;
                border-radius: 12px;
                padding: 14px 14px 14px 45px;
                font-size: 18px;
                color: #37474F;
                min-height: 28px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 2px solid #1E88E5; background-color: #FFFFFF;
            }
            QPushButton#primary {
                background-color: #1E88E5; color: white; border: none; border-radius: 12px;
                padding: 16px; font-weight: bold; font-size: 18px;
            }
            QPushButton#primary:hover { background-color: #1976D2; }
            QPushButton#secondary {
                background-color: transparent; color: #546E7A; border: none;
                font-weight: 600; font-size: 16px;
            }
            QPushButton#secondary:hover { color: #1E88E5; }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)

        container = QFrame()
        container.setObjectName("container")
        container.setFixedWidth(550)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 10)
        container.setGraphicsEffect(shadow)

        form_layout = QVBoxLayout(container)
        form_layout.setSpacing(25)
        form_layout.setContentsMargins(50, 50, 50, 50)

        title = QLabel("Đăng Ký Tài Khoản")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title)

        # Inputs
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Tên đăng nhập")
        self.username_input.addAction(self.get_icon("user.png"), QLineEdit.LeadingPosition)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mật khẩu")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.addAction(self.get_icon("lock.png"), QLineEdit.LeadingPosition)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Nhập lại mật khẩu")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.addAction(self.get_icon("lock.png"), QLineEdit.LeadingPosition)
        
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("Họ và tên")
        self.full_name_input.addAction(self.get_icon("user.png"), QLineEdit.LeadingPosition)

        row_layout = QHBoxLayout()
        row_layout.setSpacing(15)
        
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Khác", "Nam", "Nữ"])
        self.gender_input.setStyleSheet("padding-left: 15px;") 
        
        self.dob_input = QDateEdit(calendarPopup=True)
        self.dob_input.setDisplayFormat("yyyy-MM-dd")
        self.dob_input.setDate(QDate.currentDate().addYears(-18))
        self.dob_input.setStyleSheet("padding-left: 15px;")

        row_layout.addWidget(self.gender_input)
        row_layout.addWidget(self.dob_input)

        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)
        form_layout.addWidget(self.confirm_password_input)
        form_layout.addWidget(self.full_name_input)
        form_layout.addLayout(row_layout)

        form_layout.addSpacing(15)

        self.register_btn = QPushButton("ĐĂNG KÝ")
        self.register_btn.setObjectName("primary")
        self.register_btn.setCursor(Qt.PointingHandCursor)
        form_layout.addWidget(self.register_btn)

        self.back_btn = QPushButton("Đã có tài khoản? Đăng nhập ngay")
        self.back_btn.setObjectName("secondary")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        form_layout.addWidget(self.back_btn)

        self.message_label = QLabel("")
        self.message_label.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(self.message_label)

        main_layout.addWidget(container)

        self.register_btn.clicked.connect(self.do_register)
        self.back_btn.clicked.connect(self.go_to_login)

    def go_to_login(self):
        self.parent.layout.setCurrentWidget(self.parent.login_page)

    def show_message(self, message, error=True):
        color = "#D32F2F" if error else "#1E88E5"
        self.message_label.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: 600; margin-top: 5px;")
        self.message_label.setText(message)

    def do_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        full_name = self.full_name_input.text().strip()
        gender_map = {"Nam": "male", "Nữ": "female", "Khác": "other"}
        gender = gender_map.get(self.gender_input.currentText(), "other")
        dob = self.dob_input.date().toString("yyyy-MM-dd")

        if not all([username, password, confirm_password, full_name]):
            self.show_message("Vui lòng điền đầy đủ thông tin.", error=True)
            return
        
        if password != confirm_password:
            self.show_message("Mật khẩu xác nhận không khớp.", error=True)
            return

        self.register_btn.setEnabled(False)
        self.show_message("Đang tạo tài khoản...", error=False)

        def register_thread():
            try:
                crypto_client.register_and_save_key(
                    username, password, full_name=full_name, gender=gender, date_of_birth=dob
                )
                self.show_message("Đăng ký thành công!", error=False)
                self.username_input.clear()
                self.password_input.clear()
                self.confirm_password_input.clear()
                self.full_name_input.clear()
            except Exception as e:
                self.show_message(f"Lỗi đăng ký: {str(e)}", error=True)
            finally:
                self.register_btn.setEnabled(True)
        
        threading.Thread(target=register_thread, daemon=True).start()