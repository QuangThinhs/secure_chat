import os
import threading
import socketio
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, 
    QPushButton, QLabel, QFrame, QListWidgetItem, QLineEdit,
    QStackedLayout, QGraphicsDropShadowEffect, QAbstractItemView
)
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QBrush
from services import api_client, crypto_client

from .chat import ChatPage 
from .profile import ProfilePage
from .info_panel import InfoPanel 

SOCKET_URL = "http://127.0.0.1:5001"
sio = socketio.Client(reconnection=True)

class SocketSignals(QObject):
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    online_users_received = pyqtSignal(list)
    new_message_received = pyqtSignal(dict)
    # Signal mới: Dùng để cập nhật 1 item chat cụ thể (Thêm mới hoặc đẩy lên đầu)
    chat_updated = pyqtSignal(dict) 

class HomePage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.online_users = {}
        self.socket_connected = False
        self._socket_initialized = False
        self.current_chat_id = None 
        self.current_other_user_id = None 
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_path = os.path.join(current_dir, "assets")

        self.socket_signals = SocketSignals()
        self.init_ui()
        
        # Kết nối các tín hiệu
        self.socket_signals.connected.connect(self.on_socket_connected)
        self.socket_signals.disconnected.connect(self.on_socket_disconnected)
        self.socket_signals.online_users_received.connect(self.handle_online_users)
        self.socket_signals.new_message_received.connect(self.handle_new_message)
        self.socket_signals.chat_updated.connect(self.upsert_chat_item) # <--- Kết nối signal mới

    def get_icon(self, name):
        path = os.path.join(self.assets_path, name)
        if os.path.exists(path): return QIcon(path)
        return QIcon()

    def get_status_icon(self, is_online):
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor("#4CAF50") if is_online else QColor("#B0BEC5")
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(3, 3, 10, 10)
        painter.end()
        return QIcon(pixmap)

    def init_ui(self):
        # --- CSS FONT 18px ---
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', sans-serif;
                background-color: #F0F4F8;
                color: #263238;
                font-size: 18px; /* Font to */
            }
            QFrame#sidebar {
                background-color: #FFFFFF;
                border-right: 1px solid #CFD8DC;
            }
            QLineEdit#search_bar {
                background-color: #F5F7FA;
                border: 1px solid #CFD8DC;
                border-radius: 20px;
                padding: 12px 18px 12px 40px;
                font-size: 18px;
            }
            QLineEdit#search_bar:focus {
                border: 1px solid #1E88E5;
                background-color: #FFFFFF;
            }
            QLabel.section_title {
                color: #78909C;
                font-size: 16px;
                font-weight: bold;
                text-transform: uppercase;
                margin-top: 25px;
                padding-left: 20px;
            }
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 16px; 
                border-radius: 12px;
                margin: 5px 12px;
                color: #37474F;
                font-weight: 500;
                font-size: 18px;
            }
            QListWidget::item:hover { background-color: #F5F7FA; }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                color: #1565C0;
            }
            QFrame#user_footer {
                background-color: #FFFFFF;
                border-top: 1px solid #CFD8DC;
            }
            QPushButton#profile_btn {
                background-color: transparent;
                border: none;
                text-align: left;
                padding: 12px;
                font-weight: bold;
                color: #263238;
                font-size: 18px;
            }
            QPushButton#profile_btn:hover { background-color: #F5F7FA; }
            QPushButton#logout_btn {
                background-color: #FFEBEE;
                border-radius: 8px;
                border: none;
            }
            QPushButton#logout_btn:hover { background-color: #FFCDD2; }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. SIDEBAR
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(380)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(2, 0)
        sidebar.setGraphicsEffect(shadow)
        sidebar.raise_()

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header (Search)
        sidebar_header = QFrame()
        sidebar_header.setFixedHeight(90)
        header_layout = QVBoxLayout(sidebar_header)
        header_layout.setContentsMargins(20, 20, 20, 0)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Tìm kiếm...")
        self.search_bar.setObjectName("search_bar")
        self.search_bar.addAction(self.get_icon("search.png"), QLineEdit.LeadingPosition)
        header_layout.addWidget(self.search_bar)
        sidebar_layout.addWidget(sidebar_header)

        # Lists
        list_layout = QVBoxLayout()
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_chat = QLabel("  Tin nhắn")
        lbl_chat.setProperty("class", "section_title")
        list_layout.addWidget(lbl_chat)

        self.chat_list = QListWidget()
        self.chat_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.chat_list.itemClicked.connect(self.on_chat_clicked)
        list_layout.addWidget(self.chat_list, 2)

        lbl_online = QLabel("  Đang hoạt động")
        lbl_online.setProperty("class", "section_title")
        list_layout.addWidget(lbl_online)

        self.online_list = QListWidget()
        self.online_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.online_list.itemClicked.connect(self.start_chat_with_user)
        list_layout.addWidget(self.online_list, 1)

        sidebar_layout.addLayout(list_layout)

        # Footer
        user_footer = QFrame()
        user_footer.setObjectName("user_footer")
        footer_layout = QHBoxLayout(user_footer)
        footer_layout.setContentsMargins(20, 20, 20, 20)
        
        self.profile_btn = QPushButton("  Tôi")
        self.profile_btn.setObjectName("profile_btn")
        self.profile_btn.setIcon(self.get_icon("user.png"))
        self.profile_btn.setIconSize(QSize(32, 32))
        self.profile_btn.setCursor(Qt.PointingHandCursor)
        
        self.logout_btn = QPushButton()
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.setIcon(self.get_icon("logout.png"))
        self.logout_btn.setFixedSize(50, 50)
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setToolTip("Đăng xuất")

        footer_layout.addWidget(self.profile_btn, 1)
        footer_layout.addWidget(self.logout_btn)
        
        sidebar_layout.addWidget(user_footer)
        main_layout.addWidget(sidebar)

        # 2. CONTENT STACK
        content_frame = QFrame()
        content_frame.setStyleSheet("background-color: #F0F4F8;")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.content_stack = QStackedLayout()
        
        # Placeholder
        placeholder_widget = QWidget()
        p_layout = QVBoxLayout(placeholder_widget)
        p_layout.setAlignment(Qt.AlignCenter)
        
        p_icon = QLabel()
        logo = QPixmap(os.path.join(self.assets_path, "logo.png"))
        if not logo.isNull():
            p_icon.setPixmap(logo.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            p_icon.setStyleSheet("opacity: 0.3;")
        p_layout.addWidget(p_icon, 0, Qt.AlignCenter)
        
        p_text = QLabel("Chọn một cuộc hội thoại để bắt đầu")
        p_text.setStyleSheet("color: #90A4AE; font-size: 24px; margin-top: 25px; font-weight: 500;")
        p_layout.addWidget(p_text, 0, Qt.AlignCenter)
        
        self.content_stack.addWidget(placeholder_widget)

        # Chat Page
        self.chat_page = ChatPage(self)
        self.content_stack.addWidget(self.chat_page)
        
        content_layout.addLayout(self.content_stack)
        main_layout.addWidget(content_frame, 1)

        # 3. INFO PANEL
        self.info_panel = InfoPanel(self.parent) 
        self.info_panel.close_btn.clicked.connect(self.toggle_info_panel)
        self.info_panel.hide()
        main_layout.addWidget(self.info_panel)

        self.search_bar.textChanged.connect(self.filter_lists)
        self.profile_btn.clicked.connect(self.show_profile)
        self.logout_btn.clicked.connect(self.logout)
        self.chat_page.info_button.clicked.connect(self.toggle_info_panel)

    # --- LOGIC MỚI: CẬP NHẬT CHAT NÓNG (HOT UPDATE) ---
    
    def upsert_chat_item(self, chat_data):
        """
        Hàm này chạy trên GUI Thread thông qua Signal.
        Nó sẽ tìm chat trong list:
        - Nếu có: Đẩy lên đầu, in đậm, đổi màu.
        - Nếu chưa: Tạo mới, chèn vào đầu, in đậm, đổi màu.
        """
        chat_id = chat_data["chat_id"]
        name = chat_data.get("name", "Chat")
        unread = chat_data.get("unread_count", 1) # Mặc định là 1 nếu tin mới đến

        # 1. Tìm xem item đã tồn tại chưa
        existing_item = None
        row = -1
        for i in range(self.chat_list.count()):
            item = self.chat_list.item(i)
            if item.data(Qt.UserRole) == chat_id:
                existing_item = item
                row = i
                break
        
        # 2. Xóa item cũ nếu có (để lát chèn lên đầu)
        if existing_item:
            self.chat_list.takeItem(row)
        
        # 3. Tạo item mới (hoặc tái sử dụng)
        display_text = f"{name}"
        if unread > 0:
             display_text += f"   ({unread})" # Thêm số lượng tin nhắn

        new_item = QListWidgetItem(display_text)
        new_item.setIcon(self.get_icon("logo.png"))
        new_item.setData(Qt.UserRole, chat_id)
        
        # 4. Style: In đậm và Màu xanh
        font = new_item.font()
        font.setBold(True)
        new_item.setFont(font)
        new_item.setForeground(QColor("#1E88E5"))
        
        # 5. Chèn vào đầu danh sách (Index 0)
        self.chat_list.insertItem(0, new_item)

    def fetch_specific_chat(self, chat_id):
        """Hàm chạy trong thread phụ để lấy thông tin chat"""
        status, chat = api_client.get_chat_detail(self.parent.token, chat_id)
        if status == 200:
            # Giả lập unread = 1 để kích hoạt in đậm (vì tin mới vừa tới)
            chat["unread_count"] = 1 
            self.socket_signals.chat_updated.emit(chat)

    # --------------------------------------------------

    def update_online_list(self):
        self.online_list.clear()
        for uid in self.online_users.keys():
            status, data = api_client.get_user_info(self.parent.token, uid)
            name = f"User {uid}" 
            if status == 200:
                name = data.get("full_name") or data.get("username")
            
            item = QListWidgetItem(name)
            item.setIcon(self.get_status_icon(True)) 
            item.setData(Qt.UserRole, uid)
            self.online_list.addItem(item)
            self.filter_lists()

    def refresh_chats(self):
        status, chats = api_client.get_chats(self.parent.token)
        self.chat_list.clear()
        if status == 200:
            chats_sorted = sorted(chats, key=lambda c: c.get('unread_count', 0), reverse=True)
            for c in chats_sorted:
                name = c['name']
                unread = c.get('unread_count', 0)
                
                if unread > 0:
                    display_text = f"{name}   ({unread})"
                else:
                    display_text = name

                item = QListWidgetItem(display_text)
                item.setIcon(self.get_icon("logo.png"))
                item.setData(Qt.UserRole, c["chat_id"])
                
                font = item.font()
                if unread > 0:
                    font.setBold(True)
                    item.setForeground(QColor("#1E88E5"))
                else:
                    font.setBold(False)
                    item.setForeground(QColor("#37474F"))
                
                item.setFont(font)
                self.chat_list.addItem(item)
                
                if c["chat_id"] == self.current_chat_id:
                    self.chat_list.setCurrentItem(item)
            self.filter_lists()

    def set_current_user_label(self):
        if self.parent.user_id:
            status, data = api_client.get_user_info(self.parent.token, self.parent.user_id)
            if status == 200:
                name = data.get("full_name") or self.parent.user_id
                self.profile_btn.setText(f"  {name}")
            else:
                self.profile_btn.setText(f"  User {self.parent.user_id}")

    def on_socket_connected(self):
        self.socket_connected = True
        print("[Socket] Kết nối thành công")

    def on_socket_disconnected(self):
        self.socket_connected = False
        print("[Socket] Mất kết nối")

    def handle_online_users(self, users):
        self.online_users = {uid: True for uid in users if uid != self.parent.user_id}
        self.update_online_list()

    def handle_new_message(self, msg):
        chat_id = msg["chat_id"]
        sender = msg["sender_id"]
        
        # TRƯỜNG HỢP 1: Đang mở chat này -> Hiện tin nhắn
        if self.content_stack.currentWidget() == self.chat_page and self.current_chat_id == chat_id:
            try:
                key_dict = msg["aes_key_encrypted"]
                wrapped = key_dict.get(str(self.parent.user_id))
                if wrapped:
                    aes_key = crypto_client.unwrap_aes_key(wrapped, self.parent.private_key)
                    text = crypto_client.decrypt_aes_gcm(msg["content"], aes_key, msg["iv"], msg["tag"])
                else:
                    text = "[Không có khóa giải mã]"
            except Exception as e:
                text = f"[Lỗi: {e}]"
            self.chat_page.add_message(sender, text, sender == self.parent.user_id)
            
            # Vẫn đánh dấu đã đọc
            token = self.parent.token
            threading.Thread(target=api_client.mark_chat_read, args=(token, chat_id), daemon=True).start()
        
        # TRƯỜNG HỢP 2: Chat khác / Chat mới -> CẬP NHẬT LIST NGAY LẬP TỨC
        else:
            # Kiểm tra xem chat đã có trong list chưa
            found = False
            for i in range(self.chat_list.count()):
                item = self.chat_list.item(i)
                if item.data(Qt.UserRole) == chat_id:
                    # Nếu có rồi -> Lấy thông tin hiện tại để đẩy lên
                    chat_name = item.text().split("   (")[0] # Lấy tên gốc
                    # Giả lập dữ liệu để đẩy lên đầu
                    chat_data = {"chat_id": chat_id, "name": chat_name, "unread_count": 1} # Tạm thời +1
                    self.upsert_chat_item(chat_data)
                    found = True
                    break
            
            # Nếu chưa có -> Phải gọi API lấy tên chat rồi mới add vào
            if not found:
                threading.Thread(target=self.fetch_specific_chat, args=(chat_id,), daemon=True).start()

    def filter_lists(self):
        search_text = self.search_bar.text().lower().strip()
        for i in range(self.chat_list.count()):
            item = self.chat_list.item(i)
            item.setHidden(search_text not in item.text().lower())
        for i in range(self.online_list.count()):
            item = self.online_list.item(i)
            item.setHidden(search_text not in item.text().lower())

    def show_profile(self):
        profile_dialog = ProfilePage(self.parent)
        profile_dialog.exec_()

    def toggle_info_panel(self):
        if self.info_panel.isVisible():
            self.info_panel.hide()
        else:
            if self.current_other_user_id:
                self.info_panel.load_user_info(self.current_other_user_id)
                self.info_panel.show()
            else:
                print("Không có thông tin user để hiển thị")

    def on_chat_clicked(self, item):
        chat_id = item.data(Qt.UserRole)
        self.current_chat_id = chat_id
        self.info_panel.hide()
        
        # Reset hiển thị về bình thường (bỏ bold, bỏ số)
        font = item.font()
        font.setBold(False)
        item.setFont(font)
        item.setForeground(QColor("#37474F"))
        txt = item.text().split("   (")[0]
        item.setText(txt)
        
        token = self.parent.token
        if token and chat_id:
            threading.Thread(target=api_client.mark_chat_read, args=(token, chat_id), daemon=True).start()

        self.chat_page.load_chat(chat_id)
        self.content_stack.setCurrentWidget(self.chat_page)

    def start_chat_with_user(self, item):
        uid = item.data(Qt.UserRole)
        if uid == self.parent.user_id: return
        status, chat = api_client.create_chat(self.parent.token, name=f"Chat {uid}", is_group=False, members=[uid])
        if status in (200, 201):
            chat_id = chat["chat_id"]
            self.current_chat_id = chat_id
            self.info_panel.hide()
            self.chat_page.load_chat(chat_id)
            self.content_stack.setCurrentWidget(self.chat_page)
            # Thêm chat vào list ngay lập tức
            self.upsert_chat_item({"chat_id": chat_id, "name": chat["name"], "unread_count": 0})

    def logout(self):
        try: 
            if self.socket_connected: sio.disconnect()
            self._socket_initialized = False 
            self.socket_connected = False
        except: pass
        api_client.logout(self.parent.token)
        self.parent.token = None
        self.parent.user_id = None
        self.parent.private_key = None
        self.current_other_user_id = None
        self.chat_page.clear_chat()
        self.parent.layout.setCurrentWidget(self.parent.login_page)

    def connect_socket(self):
        if self._socket_initialized:
            try: 
                if not self.socket_connected: sio.connect(SOCKET_URL, auth={"token": self.parent.token}, wait_timeout=5)
            except: pass
            return
        self._socket_initialized = True
        def _connect():
            try: sio.connect(SOCKET_URL, auth={"token": self.parent.token}, wait_timeout=10)
            except Exception as e: print(f"Socket connect err: {e}")
        threading.Thread(target=_connect, daemon=True).start()

        @sio.on("connect")
        def on_connect(): self.socket_signals.connected.emit()
        @sio.on("disconnect")
        def on_disconnect(): self.socket_signals.disconnected.emit()
        @sio.on("online_users")
        def on_online(users): self.socket_signals.online_users_received.emit(users)
        @sio.on("receive_message")
        def on_receive(msg): self.socket_signals.new_message_received.emit(msg)