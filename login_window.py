from PySide6.QtWidgets import (
    QDialog, QLineEdit, QPushButton, QVBoxLayout,
    QLabel, QMessageBox,
)
from main import MainWindow

def validate_login(raw: str):
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
        self.main_window: MainWindow | None = None
        self.setWindowTitle("Авторизация — Мир киберспорта")
        self.setup_ui()

    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        self.login_input.returnPressed.connect(self.check_login)

        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.check_login)

        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.login_input)
        layout.addWidget(self.login_button)

    def check_login(self) -> None:
        login, error = validate_login(self.login_input.text())
        if error:
            QMessageBox.critical(self, "Ошибка", error)
            return

        try:
            row = self.db.fetch_user_by_login(login)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка при запросе: {e}")
            return

        if row is None:
            QMessageBox.critical(
                self, "Ошибка авторизации", "Пользователь не найден"
            )
            return

        user_id, role_id, last_name, first_name, middle_name = row

        parts = [last_name, first_name]
        if middle_name:
            parts.append(middle_name)
        full_name = " ".join(parts)

        role_names = {
            1: "Администратор",
            2: "Менеджер",
            3: "Авторизованный пользователь",
        }
        role_name = role_names.get(role_id, f"Роль {role_id}")

        QMessageBox.information(
            self, "Информация", f"Добро пожаловать, {full_name}!"
        )

        self.main_window = MainWindow(
            db=self.db,
            user_id=user_id,
            role_id=role_id,
            role_name=role_name,
            full_name=full_name,
        )
        self.main_window.show()
        self.accept()