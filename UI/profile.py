from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, 
    QDateEdit, QTextEdit, QMessageBox, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QDate
from services import api_client

class ProfilePage(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_app = parent 
        self.setWindowTitle("Chỉnh sửa hồ sơ")
        self.setMinimumSize(500, 550)
        self.init_ui()
        self.load_profile_data()

    def init_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                font-family: 'Segoe UI';
                font-size: 18px; /* Font to */
            }
            QLineEdit, QComboBox, QDateEdit, QTextEdit {
                background-color: #FAFAFA;
                border: 1px solid #CFD8DC;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton {
                background-color: #1E88E5;
                color: white;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1976D2; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)
        
        self.username_label = QLineEdit()
        self.username_label.setReadOnly(True)
        self.username_label.setStyleSheet("background-color: #ECEFF1; color: #546E7A;")
        
        self.full_name_input = QLineEdit()
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Khác", "Nam", "Nữ"])
        
        self.dob_input = QDateEdit(calendarPopup=True)
        self.dob_input.setDisplayFormat("yyyy-MM-dd")
        
        self.bio_input = QTextEdit()
        self.bio_input.setFixedHeight(120)
        self.bio_input.setPlaceholderText("Giới thiệu bản thân...")

        form.addRow("Tên đăng nhập:", self.username_label)
        form.addRow("Họ và tên:", self.full_name_input)
        form.addRow("Giới tính:", self.gender_input)
        form.addRow("Ngày sinh:", self.dob_input)
        form.addRow("Tiểu sử:", self.bio_input)
        
        layout.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Save).setText("Lưu")
        btns.button(QDialogButtonBox.Cancel).setText("Hủy")
        btns.accepted.connect(self.save_profile)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def load_profile_data(self):
        token = self.parent_app.token
        user_id = self.parent_app.user_id
        status, data = api_client.get_user_info(token, user_id)
        if status == 200:
            self.username_label.setText(data.get("username", ""))
            self.full_name_input.setText(data.get("full_name", ""))
            self.bio_input.setPlainText(data.get("bio", ""))
            
            gender_map = {"other": "Khác", "male": "Nam", "female": "Nữ"}
            g_val = gender_map.get(data.get("gender", "other"), "Khác")
            idx = self.gender_input.findText(g_val, Qt.MatchFixedString)
            if idx >= 0: self.gender_input.setCurrentIndex(idx)
            
            dob = data.get("date_of_birth")
            if dob: self.dob_input.setDate(QDate.fromString(dob, "yyyy-MM-dd"))

    def save_profile(self):
        token = self.parent_app.token
        
        gender_map_rev = {"Nam": "male", "Nữ": "female", "Khác": "other"}
        gender = gender_map_rev.get(self.gender_input.currentText(), "other")
        
        status, data = api_client.update_profile(
            token,
            full_name=self.full_name_input.text().strip(),
            gender=gender,
            date_of_birth=self.dob_input.date().toString("yyyy-MM-dd"),
            bio=self.bio_input.toPlainText().strip()
        )
        if status == 200:
            QMessageBox.information(self, "Thành công", "Đã cập nhật hồ sơ.")
            self.accept()
        else:
            QMessageBox.warning(self, "Lỗi", f"Cập nhật thất bại: {data.get('msg')}")   