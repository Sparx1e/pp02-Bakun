from PySide6.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QMessageBox
from main import MainWindow

class LoginWindow(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Авторизация - Мир киберспорта")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Задание 2: Поле для логина
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.login_input)
        
        # Задание 3: Кнопка «Войти»
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.check_login)
        layout.addWidget(self.login_button)
        
        self.setLayout(layout)

    # Задание 4: Проверка логина в БД
    def check_login(self):
        login = self.login_input.text().strip()
        
        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин")
            return
            
        try:
            self.db.cursor.execute("SELECT user_id, role_id FROM users WHERE login = %s", (login,))
            result = self.db.cursor.fetchone()
            
            if result:
                user_id, role_id = result
                self.accept() 
                
                # Задание 5: Передача user_id и role_id в MainWindow
                self.main_window = MainWindow(user_id=user_id, role_id=role_id)
                self.main_window.show()
            else:
                QMessageBox.warning(self, "Ошибка", "Пользователь не найден")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка при запросе: {e}")