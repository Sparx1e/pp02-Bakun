from PySide6.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QMessageBox
from main import MainWindow

def validate_login(raw):
    login = raw.strip()
    if not login:
        return None, "Введите логин (пробелы не считаются)"
    if len(login) < 3:
        return None, "Логин должен содержать минимум 3 символа"
    return login, None

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
        self.login_button.clicked.connect(self.check_login)
        layout.addWidget(self.login_button)
        
        self.setLayout(layout)

    def check_login(self):
        login, error = validate_login(self.login_input.text())
        if error:
            QMessageBox.critical(self, "Ошибка", error)
            return

        try:
            self.db.cursor.execute(
                "SELECT user_id, role_id, last_name, first_name, middle_name "
                "FROM users WHERE login = %s",
                (login,)
            )
            result = self.db.cursor.fetchone()

            if result is None:
                QMessageBox.critical(self, "Ошибка авторизации", "Пользователь не найден")
                return

            user_id, role_id, last_name, first_name, middle_name = result

            parts = [last_name, first_name]
            if middle_name:
                parts.append(middle_name)
            full_name = " ".join(parts)

            QMessageBox.information(self, "Информация", f"Добро пожаловать, {full_name}!")

            self.main_window = MainWindow(
                db=self.db, 
                user_id=user_id,
                role_id=role_id,
                full_name=full_name
            )
            self.main_window.show()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка при запросе: {e}")