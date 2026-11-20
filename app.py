import sys
from PySide6.QtWidgets import QApplication
from db import Database
from login_window import LoginWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    db = Database()
    if db.connect():
        login_window = LoginWindow(db)
        if login_window.exec() != LoginWindow.accepted:
            sys.exit(0) # При отмене входа главное окно не создается, программа завершается
        sys.exit(app.exec())
    else:
        print("Не удалось подключиться к базе данных.")