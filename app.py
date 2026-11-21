import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from db import Database
from login_window import LoginWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("PP02")
    app.setOrganizationName("PP02")

    db = Database()
    if not db.connect():
        QMessageBox.critical(
            None, "Ошибка", "Не удалось подключиться к базе данных."
        )
        return 1

    login_window = LoginWindow(db)
    if login_window.exec() != LoginWindow.DialogCode.Accepted:
        db.close()
        return 0

    code = app.exec()
    db.close()
    return code


if __name__ == "__main__":
    sys.exit(main())