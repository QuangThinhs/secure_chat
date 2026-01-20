import os
import threading
import socketio
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QPushButton, 
    QLabel, QFrame, QListWidgetItem, QLineEdit, QStackedLayout, 
    QGraphicsDropShadowEffect, QAbstractItemView, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QBrush, QPen
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
        self.socket_signals.chat_updated.connect(self.upsert_chat_item)
    
    def get_icon(self, name):
        path = os.path.join(self.assets_path, name)
        if os.path.exists(path):
            return QIcon(path)
        return QIcon()
    
    def get_status_icon(self, is_online):
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Vẽ viền trắng
        painter.setPen(QPen(QColor("#FFFFFF"), 2))
        painter.setBrush(QBrush(QColor("#4CAF50") if is_online else QColor("#9E9E9E")))
        painter.drawEllipse(2, 2, 16, 16)
        painter.end()
        return QIcon(pixmap)
    
    def init_ui(self):
        # Modern CSS với gradient và animations
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', 'San Francisco', 'Helvetica Neue', sans-serif;
                background-color: #F8FAFC;
                color: #1E293B;
                font-size: 15px;
            }
            
            QFrame#sidebar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8FAFC);
                border-right: 1px solid #E2E8F0;
            }
            
            QFrame#sidebar_header {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6366F1, stop:1 #8B5CF6);
                border: none;
            }
            
            QLineEdit#search_bar {
                background-color: rgba(255, 255, 255, 0.95);
                border: 2px solid #E0E7FF;
                border-radius: 24px;
                padding: 14px 20px 14px 48px;
                font-size: 15px;
                color: #1E293B;
            }
            
            QLineEdit#search_bar:focus {
                border: 2px solid #6366F1;
                background-color: #FFFFFF;
            }
            
            QLabel.section_title {
                color: #64748B;
                font-size: 13px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-top: 20px;
                margin-bottom: 8px;
                padding-left: 20px;
            }
            
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
                padding: 0px 8px;
            }
            
            QListWidget::item {
                padding: 14px 16px;
                border-radius: 14px;
                margin: 4px 0px;
                color: #334155;
                font-weight: 500;
                font-size: 15px;
                border: 1px solid transparent;
            }
            
            QListWidget::item:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #F1F5F9, stop:1 #E0E7FF);
                border: 1px solid #C7D2FE;
            }
            
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #EEF2FF, stop:1 #E0E7FF);
                color: #4F46E5;
                border: 1px solid #A5B4FC;
            }
            
            QFrame#user_footer {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #F8FAFC);
                border-top: 1px solid #E2E8F0;
            }
            
            QPushButton#profile_btn {
                background-color: transparent;
                border: none;
                text-align: left;
                padding: 14px 16px;
                font-weight: 600;
                color: #1E293B;
                font-size: 15px;
                border-radius: 12px;
            }
            
            QPushButton#profile_btn:hover {
                background-color: #F1F5F9;
            }
            
            QPushButton#logout_btn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FEE2E2, stop:1 #FECACA);
                border-radius: 12px;
                border: 1px solid #FCA5A5;
            }
            
            QPushButton#logout_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FECACA, stop:1 #FCA5A5);
            }
            
            QLabel#app_title {
                color: #FFFFFF;
                font-size: 22px;
                font-weight: 700;
                padding: 20px;
            }
            
            QLabel#connection_status {
                color: rgba(255, 255, 255, 0.9);
                font-size: 12px;
                padding: 0px 20px 16px 20px;
            }
        """)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. SIDEBAR với shadow đẹp hơn
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(360)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(4, 0)
        sidebar.setGraphicsEffect(shadow)
        sidebar.raise_()
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Header gradient với app title
        sidebar_header = QFrame()
        sidebar_header.setObjectName("sidebar_header")
        sidebar_header.setFixedHeight(140)
        
        header_layout = QVBoxLayout(sidebar_header)
        header_layout.setContentsMargins(0, 0, 0, 16)
        
        # App Title
        app_title = QLabel("💬 ChatApp")
        app_title.setObjectName("app_title")
        header_layout.addWidget(app_title)
        
        # Connection Status
        self.connection_status = QLabel("● Đang kết nối...")
        self.connection_status.setObjectName("connection_status")
        header_layout.addWidget(self.connection_status)
        
        # Search bar
        search_container = QWidget()
        search_container.setStyleSheet("background: transparent;")
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(16, 0, 16, 0)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Tìm kiếm...")
        self.search_bar.setObjectName("search_bar")
        search_layout.addWidget(self.search_bar)
        
        header_layout.addWidget(search_container)
        sidebar_layout.addWidget(sidebar_header)
        
        # Lists với spacing đẹp hơn
        list_container = QWidget()
        list_container.setStyleSheet("background: transparent;")
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 12, 0, 0)
        list_layout.setSpacing(0)
        
        # Chat List
        lbl_chat = QLabel("💬 TIN NHẮN")
        lbl_chat.setProperty("class", "section_title")
        list_layout.addWidget(lbl_chat)
        
        self.chat_list = QListWidget()
        self.chat_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.chat_list.itemClicked.connect(self.on_chat_clicked)
        list_layout.addWidget(self.chat_list, 3)
        
        # Online List
        lbl_online = QLabel("🟢 ĐANG HOẠT ĐỘNG")
        lbl_online.setProperty("class", "section_title")
        list_layout.addWidget(lbl_online)
        
        self.online_list = QListWidget()
        self.online_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.online_list.itemClicked.connect(self.start_chat_with_user)
        list_layout.addWidget(self.online_list, 2)
        
        sidebar_layout.addWidget(list_container)
        
        # Footer với style mới
        user_footer = QFrame()
        user_footer.setObjectName("user_footer")
        user_footer.setFixedHeight(80)
        
        footer_layout = QHBoxLayout(user_footer)
        footer_layout.setContentsMargins(16, 16, 16, 16)
        footer_layout.setSpacing(12)
        
        self.profile_btn = QPushButton("👤 Tôi")
        self.profile_btn.setObjectName("profile_btn")
        self.profile_btn.setIconSize(QSize(24, 24))
        self.profile_btn.setCursor(Qt.PointingHandCursor)
        self.profile_btn.setFixedHeight(48)
        
        self.logout_btn = QPushButton("🚪")
        self.logout_btn.setObjectName("logout_btn")
        self.logout_btn.setFixedSize(48, 48)
        self.logout_btn.setCursor(Qt.PointingHandCursor)
        self.logout_btn.setToolTip("Đăng xuất")
        
        footer_layout.addWidget(self.profile_btn, 1)
        footer_layout.addWidget(self.logout_btn)
        
        sidebar_layout.addWidget(user_footer)
        main_layout.addWidget(sidebar)
        
        # 2. CONTENT STACK với background đẹp hơn
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #F8FAFC, stop:1 #EEF2FF);
            }
        """)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.content_stack = QStackedLayout()
        
        # Placeholder với thiết kế đẹp hơn
        placeholder_widget = QWidget()
        placeholder_widget.setStyleSheet("background: transparent;")
        p_layout = QVBoxLayout(placeholder_widget)
        p_layout.setAlignment(Qt.AlignCenter)
        
        # Icon container
        icon_container = QFrame()
        icon_container.setFixedSize(200, 200)
        icon_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #E0E7FF, stop:1 #DDD6FE);
                border-radius: 100px;
            }
        """)
        
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setAlignment(Qt.AlignCenter)
        
        p_icon = QLabel("💬")
        p_icon.setStyleSheet("""
            color: #6366F1; 
            font-size: 80px;
            background: transparent;
        """)
        icon_layout.addWidget(p_icon, 0, Qt.AlignCenter)
        
        p_layout.addWidget(icon_container, 0, Qt.AlignCenter)
        
        p_text = QLabel("Chọn một cuộc hội thoại để bắt đầu")
        p_text.setStyleSheet("""
            color: #64748B; 
            font-size: 20px; 
            font-weight: 600;
            margin-top: 32px;
            background: transparent;
        """)
        p_layout.addWidget(p_text, 0, Qt.AlignCenter)
        
        p_subtext = QLabel("Hoặc bắt đầu trò chuyện với người dùng đang online")
        p_subtext.setStyleSheet("""
            color: #94A3B8; 
            font-size: 14px;
            margin-top: 8px;
            background: transparent;
        """)
        p_layout.addWidget(p_subtext, 0, Qt.AlignCenter)
        
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
        
        # Connect signals
        self.search_bar.textChanged.connect(self.filter_lists)
        self.profile_btn.clicked.connect(self.show_profile)
        self.logout_btn.clicked.connect(self.logout)
        self.chat_page.info_button.clicked.connect(self.toggle_info_panel)
    
    def upsert_chat_item(self, chat_data):
        """Cập nhật hoặc thêm mới chat item"""
        chat_id = chat_data["chat_id"]
        name = chat_data.get("name", "Chat")
        unread = chat_data.get("unread_count", 1)
        
        # Tìm item hiện có
        existing_item = None
        row = -1
        for i in range(self.chat_list.count()):
            item = self.chat_list.item(i)
            if item.data(Qt.UserRole) == chat_id:
                existing_item = item
                row = i
                break
        
        # Xóa item cũ nếu có
        if existing_item:
            self.chat_list.takeItem(row)
        
        # Tạo item mới
        display_text = f"{name}"
        if unread > 0:
            display_text = f"🔴 {name} ({unread})"
        
        new_item = QListWidgetItem(display_text)
        new_item.setIcon(self.get_icon("logo.png"))
        new_item.setData(Qt.UserRole, chat_id)
        
        # Style
        font = new_item.font()
        font.setBold(unread > 0)
        new_item.setFont(font)
        
        if unread > 0:
            new_item.setForeground(QColor("#4F46E5"))
        
        # Chèn vào đầu
        self.chat_list.insertItem(0, new_item)
    
    def fetch_specific_chat(self, chat_id):
        """Lấy thông tin chi tiết chat"""
        status, chat = api_client.get_chat_detail(self.parent.token, chat_id)
        if status == 200:
            chat["unread_count"] = 1
            self.socket_signals.chat_updated.emit(chat)
    
    def update_online_list(self):
        """Cập nhật danh sách người dùng online"""
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
        """Làm mới danh sách chat"""
        status, chats = api_client.get_chats(self.parent.token)
        self.chat_list.clear()
        
        if status == 200:
            chats_sorted = sorted(chats, key=lambda c: c.get('unread_count', 0), reverse=True)
            
            for c in chats_sorted:
                name = c['name']
                unread = c.get('unread_count', 0)
                
                if unread > 0:
                    display_text = f"🔴 {name} ({unread})"
                else:
                    display_text = name
                
                item = QListWidgetItem(display_text)
                item.setIcon(self.get_icon("logo.png"))
                item.setData(Qt.UserRole, c["chat_id"])
                
                font = item.font()
                font.setBold(unread > 0)
                item.setFont(font)
                
                if unread > 0:
                    item.setForeground(QColor("#4F46E5"))
                else:
                    item.setForeground(QColor("#334155"))
                
                self.chat_list.addItem(item)
                
                if c["chat_id"] == self.current_chat_id:
                    self.chat_list.setCurrentItem(item)
        
        self.filter_lists()
    
    def set_current_user_label(self):
        """Cập nhật label người dùng hiện tại"""
        if self.parent.user_id:
            status, data = api_client.get_user_info(self.parent.token, self.parent.user_id)
            if status == 200:
                name = data.get("full_name") or self.parent.user_id
                self.profile_btn.setText(f"👤 {name}")
            else:
                self.profile_btn.setText(f"👤 User {self.parent.user_id}")
    
    def on_socket_connected(self):
        """Xử lý khi socket kết nối"""
        self.socket_connected = True
        self.connection_status.setText("● Đã kết nối")
        self.connection_status.setStyleSheet("""
            color: #4ADE80;
            font-size: 12px;
            padding: 0px 20px 16px 20px;
            font-weight: 600;
        """)
    
    def on_socket_disconnected(self):
        """Xử lý khi socket mất kết nối"""
        self.socket_connected = False
        self.connection_status.setText("● Mất kết nối")
        self.connection_status.setStyleSheet("""
            color: #F87171;
            font-size: 12px;
            padding: 0px 20px 16px 20px;
            font-weight: 600;
        """)
    
    def handle_online_users(self, users):
        """Xử lý danh sách người dùng online"""
        self.online_users = {uid: True for uid in users if uid != self.parent.user_id}
        self.update_online_list()
    
    def handle_new_message(self, msg):
        """Xử lý tin nhắn mới"""
        chat_id = msg["chat_id"]
        sender = msg["sender_id"]
        
        # Nếu đang mở chat này
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
            
            # Đánh dấu đã đọc
            token = self.parent.token
            threading.Thread(target=api_client.mark_chat_read, args=(token, chat_id), daemon=True).start()
        else:
            # Chat khác - cập nhật list
            found = False
            for i in range(self.chat_list.count()):
                item = self.chat_list.item(i)
                if item.data(Qt.UserRole) == chat_id:
                    chat_name = item.text().split(" (")[0].replace("🔴 ", "")
                    chat_data = {"chat_id": chat_id, "name": chat_name, "unread_count": 1}
                    self.upsert_chat_item(chat_data)
                    found = True
                    break
            
            if not found:
                threading.Thread(target=self.fetch_specific_chat, args=(chat_id,), daemon=True).start()
    
    def filter_lists(self):
        """Lọc danh sách theo tìm kiếm"""
        search_text = self.search_bar.text().lower().strip()
        
        for i in range(self.chat_list.count()):
            item = self.chat_list.item(i)
            item.setHidden(search_text not in item.text().lower())
        
        for i in range(self.online_list.count()):
            item = self.online_list.item(i)
            item.setHidden(search_text not in item.text().lower())
    
    def show_profile(self):
        """Hiển thị profile"""
        profile_dialog = ProfilePage(self.parent)
        profile_dialog.exec_()
    
    def toggle_info_panel(self):
        """Bật/tắt info panel"""
        if self.info_panel.isVisible():
            self.info_panel.hide()
        else:
            if self.current_other_user_id:
                self.info_panel.load_user_info(self.current_other_user_id)
                self.info_panel.show()
    
    def on_chat_clicked(self, item):
        """Xử lý khi click vào chat"""
        chat_id = item.data(Qt.UserRole)
        self.current_chat_id = chat_id
        self.info_panel.hide()
        
        # Reset style
        font = item.font()
        font.setBold(False)
        item.setFont(font)
        item.setForeground(QColor("#334155"))
        
        txt = item.text().replace("🔴 ", "").split(" (")[0]
        item.setText(txt)
        
        # Đánh dấu đã đọc
        token = self.parent.token
        if token and chat_id:
            threading.Thread(target=api_client.mark_chat_read, args=(token, chat_id), daemon=True).start()
        
        self.chat_page.load_chat(chat_id)
        self.content_stack.setCurrentWidget(self.chat_page)
    
    def start_chat_with_user(self, item):
        """Bắt đầu chat với user"""
        uid = item.data(Qt.UserRole)
        if uid == self.parent.user_id:
            return
        
        status, chat = api_client.create_chat(
            self.parent.token, 
            name=f"Chat {uid}", 
            is_group=False, 
            members=[uid]
        )
        
        if status in (200, 201):
            chat_id = chat["chat_id"]
            self.current_chat_id = chat_id
            self.info_panel.hide()
            self.chat_page.load_chat(chat_id)
            self.content_stack.setCurrentWidget(self.chat_page)
            self.upsert_chat_item({"chat_id": chat_id, "name": chat["name"], "unread_count": 0})
    
    def logout(self):
        """Đăng xuất"""
        try:
            if self.socket_connected:
                sio.disconnect()
            self._socket_initialized = False
            self.socket_connected = False
        except:
            pass
        
        api_client.logout(self.parent.token)
        self.parent.token = None
        self.parent.user_id = None
        self.parent.private_key = None
        self.current_other_user_id = None
        self.chat_page.clear_chat()
        self.parent.layout.setCurrentWidget(self.parent.login_page)
    
    def connect_socket(self):
        """Kết nối socket"""
        if self._socket_initialized:
            try:
                if not self.socket_connected:
                    sio.connect(SOCKET_URL, auth={"token": self.parent.token}, wait_timeout=5)
            except:
                pass
            return
        
        self._socket_initialized = True
        
        def _connect():
            try:
                sio.connect(SOCKET_URL, auth={"token": self.parent.token}, wait_timeout=10)
            except Exception as e:
                print(f"Socket connect err: {e}")
        
        threading.Thread(target=_connect, daemon=True).start()
        
        @sio.on("connect")
        def on_connect():
            self.socket_signals.connected.emit()
        
        @sio.on("disconnect")
        def on_disconnect():
            self.socket_signals.disconnected.emit()
        
        @sio.on("online_users")
        def on_online(users):
            self.socket_signals.online_users_received.emit(users)
        
        @sio.on("receive_message")
        def on_receive(msg):
            self.socket_signals.new_message_received.emit(msg)