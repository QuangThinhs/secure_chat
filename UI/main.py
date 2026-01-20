import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QStackedLayout
from PyQt5.QtGui import QIcon, QFont
from .login import LoginPage
from .home import HomePage
from .register import RegisterPage

class ChatApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SecureChat - Nhắn tin bảo mật")
        self.resize(1200, 800) # Tăng kích thước cửa sổ mặc định
        self.setMinimumSize(1000, 700)
        
        # Icon App
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, "assets", "logo.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Trạng thái toàn cục
        self.token = None
        self.user_id = None
        self.private_key = None
        
        self.layout = QStackedLayout()
        self.setLayout(self.layout)

        # Khởi tạo các trang
        self.login_page = LoginPage(self)
        self.register_page = RegisterPage(self)
        self.home_page = HomePage(self)

        self.layout.addWidget(self.login_page)
        self.layout.addWidget(self.register_page)
        self.layout.addWidget(self.home_page)

        self.layout.setCurrentWidget(self.login_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # --- CÀI ĐẶT FONT CHỮ TO VÀ RÕ RÀNG ---
    font = QFont("Segoe UI", 11) # Size 11pt ~ 15px
    app.setFont(font)
    
    window = ChatApp()
    window.show()
    sys.exit(app.exec_())