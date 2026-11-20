from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self, user_id=None, role_id=None, full_name=None):
        super().__init__()
        self.user_id = user_id
        self.role_id = role_id
        self.full_name = full_name
        
        self.setWindowTitle("Главное окно - Мир киберспорта")
        self.resize(600, 400)
        
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        title_label = QLabel("Мир киберспорта")
        title_label.setAlignment(Qt.AlignCenter) # type: ignore
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #458B8B;")
        
        user_info_label = QLabel(f"Вы вошли в систему.\nID пользователя: {self.user_id}\nID роли: {self.role_id}")
        user_info_label.setAlignment(Qt.AlignCenter) # type: ignore
        
        layout.addWidget(title_label)
        layout.addWidget(user_info_label)
        central_widget.setLayout(layout)