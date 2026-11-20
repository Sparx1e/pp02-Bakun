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
        
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.login_input)
        
        self.login_button = QPushButton("Войти")
        layout.addWidget(self.login_button)
        
        self.setLayout(layout)

def check_login(self):
    login = self.login_input.text().strip()

    if not login:
        QMessageBox.critical(self, "Ошибка", "Введите логин")
        return

    try:
        self.db.cursor.execute(
            "SELECT user_id, role_id, last_name, first_name, middle_name "
            "FROM users WHERE login = %s",
            (login,)
        )
        result = self.db.cursor.fetchone()

        if result:
            user_id, role_id, last_name, first_name, middle_name = result

            parts = [last_name, first_name]
            if middle_name:
                parts.append(middle_name)
            full_name = " ".join(parts)

            QMessageBox.information(
                self,
                "Информация",
                f"Добро пожаловать, {full_name}!"
            )

            self.accept()

            self.main_window = MainWindow(
                user_id=user_id,
                role_id=role_id,
                full_name=full_name
            )
            self.main_window.show()
        else:
            QMessageBox.critical(
                self,
                "Ошибка авторизации",
                "Пользователь не найден"
            )
    except Exception as e:
        QMessageBox.critical(
            self,
            "Ошибка БД",
            f"Ошибка при запросе: {e}"
        )