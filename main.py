from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QStackedWidget, QPushButton, QMessageBox
)
class MainWindow(QMainWindow):
    def __init__(self, user_id=None, role_id=None, full_name=None):
        super().__init__()
        self.user_id = user_id
        self.role_id = role_id
        self.full_name = full_name
        
        self.setWindowTitle("Мир киберспорта")
        self.resize(800, 600)
        
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        title_label = QLabel("Мир киберспорта")
        title_label.setAlignment(Qt.AlignCenter) # type: ignore
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #458B8B;")
        
        user_info_label = QLabel(f"Вы вошли как: {self.full_name} (Роль ID: {self.role_id})")
        user_info_label.setAlignment(Qt.AlignCenter) # type: ignore
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(user_info_label)

        self.stacked_widget = QStackedWidget()
        
        self.catalog_page = QWidget()
        catalog_layout = QVBoxLayout()
        catalog_layout.addWidget(QLabel("Каталог товаров (Мир киберспорта)"))
        
        self.btn_to_product = QPushButton("Перейти к карточке товара")
        self.btn_to_orders = QPushButton("Перейти к заказам")
        catalog_layout.addWidget(self.btn_to_product)
        catalog_layout.addWidget(self.btn_to_orders)
        self.catalog_page.setLayout(catalog_layout)
        self.stacked_widget.addWidget(self.catalog_page)

        self.product_page = QWidget()
        product_layout = QVBoxLayout()
        product_layout.addWidget(QLabel("Карточка товара: Игровая мышь"))
        product_layout.addWidget(QLabel("Производство: Пиксель"))
        product_layout.addWidget(QLabel("Цена: 1490 руб."))
        self.product_page.setLayout(product_layout)
        self.stacked_widget.addWidget(self.product_page)

        self.orders_page = QWidget()
        orders_layout = QVBoxLayout()
        orders_layout.addWidget(QLabel("Заказы клиентов"))
        self.orders_page.setLayout(orders_layout)
        self.stacked_widget.addWidget(self.orders_page) 

        self.btn_to_product.clicked.connect(lambda: self.switch_page(1))
        self.btn_to_orders.clicked.connect(lambda: self.switch_page(2))

        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.go_back)

        main_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(self.back_button)

        central_widget.setLayout(main_layout)

        self.switch_page(0)

    def go_back(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index > 0:
            self.switch_page(current_index - 1)

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        
        titles = [
            "Мир киберспорта — Каталог",
            "Мир киберспорта — Карточка товара",
            "Мир киберспорта — Заказы"
        ]
        self.setWindowTitle(titles[index])
        
        if index == 0:
            self.refresh_catalog()

    def closeEvent(self, event):
        reply = QMessageBox.warning(
            self,
            "Предупреждение",
            "Вы уверены, что хотите выйти?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def refresh_catalog(self):
        if hasattr(self, "load_products"):
            self.load_products()

    def load_products(self):
        ...