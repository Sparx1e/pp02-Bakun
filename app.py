import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from db import Database
from login_window import LoginWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("PP02")
    app.setOrganizationName("PP02")

    db = Database()
    if db.connect():
        login_window = LoginWindow(db)
        if login_window.exec() != LoginWindow.accepted:
            sys.exit(0)
        sys.exit(app.exec())
    else:
        QMessageBox.critical(
            None,
            "Ошибка",
            "Не удалось подключиться к базе данных."
        )
        sys.exit(1)