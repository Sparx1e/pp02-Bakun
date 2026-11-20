from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QStackedWidget, QPushButton, QMessageBox,
    QLineEdit, QTableWidget, QTableWidgetItem,
    QComboBox, QHBoxLayout
)
from PySide6.QtGui import QPixmap 
from PySide6.QtCore import Qt 

class MainWindow(QMainWindow):
    def __init__(self, db, user_id=None, role_id=None, full_name=None):
        super().__init__()
        self.db = db 
        self.user_id = user_id
        self.role_id = role_id
        self.full_name = full_name
        
        self.setWindowTitle("Мир киберспорта")
        self.resize(800, 600)
        
        self.setup_ui()
        self.load_products()

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

        logo_label = QLabel()
        pixmap = QPixmap("logo.png")
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(300, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)) # type: ignore
            logo_label.setAlignment(Qt.AlignCenter) # type: ignore
            catalog_layout.addWidget(logo_label)

        filter_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию или описанию...")
        self.search_input.textChanged.connect(self.load_products)
        
        self.category_combo = QComboBox()
        self.category_combo.addItem("Все категории")
        self.category_combo.currentIndexChanged.connect(self.load_products)
        
        self.load_categories()

        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(self.category_combo)
        
        catalog_layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Наименование", "Описание", "Цена"])
        self.table.horizontalHeader().setStretchLastSection(True)
        catalog_layout.addWidget(self.table)
        
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
        self.load_products()

    def load_products(self):
        """Загружает или фильтрует товары с помощью ILIKE"""
        if not hasattr(self, 'search_input'):
            return

        search = self.search_input.text().strip()
        self.table.setRowCount(0)
        
        try:
            query = """
                SELECT product_id, name, description, price
                FROM products
                WHERE name ILIKE %s OR description ILIKE %s
                ORDER BY product_id;
            """
            search_pattern = f"%{search}%"
            
            self.db.cursor.execute(query, (search_pattern, search_pattern))
            products = self.db.cursor.fetchall()
            
            self.table.setRowCount(len(products))
            for row_idx, product in enumerate(products):
                self.table.setItem(row_idx, 0, QTableWidgetItem(str(product[0])))
                self.table.setItem(row_idx, 1, QTableWidgetItem(product[1]))
                self.table.setItem(row_idx, 2, QTableWidgetItem(product[2]))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(product[3])))
                
        except Exception as e:
            print(f"Ошибка при загрузке товаров: {e}")

    def load_categories(self):
        ...