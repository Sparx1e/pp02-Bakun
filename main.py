from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPushButton, QStackedWidget, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)
from product_card import ProductCard

PAGE_CATALOG = 0
PAGE_CART = 1
PAGE_ORDERS = 2

class MainWindow(QMainWindow):
    def __init__(
        self,
        db,
        user_id: int | None = None,
        role_id: int | None = None,
        role_name: str | None = None,
        full_name: str | None = None,
    ):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.role_id = role_id
        self.role_name = role_name or "Гость"
        self.full_name = full_name or "Гость"

        self.setWindowTitle("Мир киберспорта")
        self.resize(900, 640)

        self.setup_ui()
        self.load_products()

    def setup_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        title_label = QLabel("Мир киберспорта")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #458B8B;"
        )

        user_info_label = QLabel(f"Вы вошли как: {self.full_name} ({self.role_name})")
        user_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(title_label)
        main_layout.addWidget(user_info_label)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 1)

        self._build_catalog_page()
        self._build_cart_page()
        self._build_orders_page()

        self.back_button = QPushButton("← Назад в каталог")
        self.back_button.clicked.connect(self.go_back)
        main_layout.addWidget(self.back_button)

        self.switch_page(PAGE_CATALOG)

    def _build_catalog_page(self) -> None:
        self.catalog_page = QWidget()
        layout = QVBoxLayout(self.catalog_page)

        logo_label = QLabel()
        pixmap = QPixmap("logo.png")
        if not pixmap.isNull():
            logo_label.setPixmap(
                pixmap.scaled(
                    300, 100,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(logo_label)

        filter_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по названию или описанию...")
        self.search_input.textChanged.connect(self.load_products)

        self.category_combo = QComboBox()
        self.category_combo.addItem("Все категории")
        self.category_combo.currentIndexChanged.connect(self.load_products)
        self._load_categories_into_combo()

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["По возрастанию", "По убыванию"])
        self.sort_combo.currentIndexChanged.connect(self.load_products)

        filter_layout.addWidget(self.search_input, 1)
        filter_layout.addWidget(self.category_combo)
        filter_layout.addWidget(QLabel("Сортировка:"))
        filter_layout.addWidget(self.sort_combo)
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Наименование", "Описание", "Цена"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table, 1)

        self.btn_to_product = QPushButton("Открыть карточку выбранного товара")
        self.btn_to_product.clicked.connect(self.open_selected_product_card)

        self.btn_to_cart = QPushButton("Перейти в корзину")
        self.btn_to_cart.clicked.connect(lambda: self.switch_page(PAGE_CART))

        self.btn_to_orders = QPushButton("Перейти к заказам")
        self.btn_to_orders.clicked.connect(lambda: self.switch_page(PAGE_ORDERS))

        layout.addWidget(self.btn_to_product)
        layout.addWidget(self.btn_to_cart)
        layout.addWidget(self.btn_to_orders)

        self.stacked_widget.addWidget(self.catalog_page)

    def _build_cart_page(self) -> None:
        self.cart_page = QWidget()
        layout = QVBoxLayout(self.cart_page)

        cart_title = QLabel("Корзина — Мир киберспорта")
        cart_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(cart_title)

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(
            ["Наименование", "Количество", "Цена", "Сумма", "ID"]
        )
        self.cart_table.setColumnHidden(4, True)
        self.cart_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.cart_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.cart_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.cart_table, 1)

        self.total_label = QLabel("Итого: 0 ₽")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.total_label)

        btn_row = QHBoxLayout()

        self.remove_button = QPushButton("Удалить выбранный товар")
        self.remove_button.clicked.connect(self.remove_from_cart)

        self.confirm_button = QPushButton("Оформить заказ")
        self.confirm_button.clicked.connect(self.confirm_order)

        btn_row.addWidget(self.remove_button)
        btn_row.addWidget(self.confirm_button)
        layout.addLayout(btn_row)

        self.stacked_widget.addWidget(self.cart_page)

    def _build_orders_page(self) -> None:
        self.orders_page = QWidget()
        layout = QVBoxLayout(self.orders_page)
        layout.addWidget(QLabel("Заказы клиентов"))
        layout.addWidget(
            QLabel("Раздел будет реализован на следующей паре (сохранение в БД).")
        )
        self.stacked_widget.addWidget(self.orders_page)

    def go_back(self) -> None:
        if self.stacked_widget.currentIndex() != PAGE_CATALOG:
            self.switch_page(PAGE_CATALOG)

    def switch_page(self, index: int) -> None:
        self.stacked_widget.setCurrentIndex(index)
        titles = [
            "Мир киберспорта — Каталог",
            "Мир киберспорта — Корзина",
            "Мир киберспорта — Заказы",
        ]
        self.setWindowTitle(titles[index])
        if index == PAGE_CATALOG:
            self.refresh_catalog()
        elif index == PAGE_CART:
            self.update_total()

    def closeEvent(self, event) -> None:
        reply = QMessageBox.warning(
            self, "Предупреждение", "Вы уверены, что хотите выйти?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def refresh_catalog(self) -> None:
        self.load_products()

    def _load_categories_into_combo(self) -> None:
        try:
            categories = self.db.fetch_categories()
        except Exception:
            categories = []
        self.category_combo.blockSignals(True)
        for cat in categories:
            self.category_combo.addItem(cat)
        self.category_combo.blockSignals(False)

    def load_products(self, *_) -> None:
        if not hasattr(self, "search_input") or not hasattr(self, "table"):
            return

        search = self.search_input.text().strip()
        category = (
            self.category_combo.currentText()
            if hasattr(self, "category_combo")
            else "Все категории"
        )
        sort = (
            self.sort_combo.currentText()
            if hasattr(self, "sort_combo")
            else "По возрастанию"
        )

        try:
            products = self.db.fetch_products(search, category, sort)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки товаров", str(e))
            return

        self.table.setRowCount(0)
        self.table.setRowCount(len(products))
        for row_idx, product in enumerate(products):
            pid, name, description, price = product
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(pid)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(name))
            self.table.setItem(row_idx, 2, QTableWidgetItem(description))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(price)))

    def open_selected_product_card(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(
                self, "Внимание",
                "Выберите товар из списка (кликните по строке).",
            )
            return

        product_id = int(self.table.item(row, 0).text()) # type: ignore
        card = ProductCard(product_id, self)
        card.exec()

    def add_to_cart(self, name: str, quantity: int, price: float, product_id: int) -> None:
        """Добавляет товар в QTableWidget. Дубликат (name+id) увеличивает количество."""
        try:
            quantity = int(quantity)
            price = float(price)
        except (TypeError, ValueError) as e:
            QMessageBox.critical(self, "Ошибка корзины", f"Неверные данные: {e}")
            return

        existing_row = -1
        for row in range(self.cart_table.rowCount()):
            name_item = self.cart_table.item(row, 0)
            id_item = self.cart_table.item(row, 4)
            if name_item and id_item and id_item.text() == str(product_id) \
                    and name_item.text() == name:
                existing_row = row
                break

        if existing_row >= 0:
            old_qty = int(self.cart_table.item(existing_row, 1).text()) # type: ignore
            new_qty = old_qty + quantity
            self.cart_table.setItem(existing_row, 1, QTableWidgetItem(str(new_qty)))
            self.cart_table.setItem(
                existing_row, 3, QTableWidgetItem(f"{new_qty * price:.2f}")
            )
        else:
            row = self.cart_table.rowCount()
            self.cart_table.insertRow(row)
            self.cart_table.setItem(row, 0, QTableWidgetItem(str(name)))
            self.cart_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
            self.cart_table.setItem(row, 2, QTableWidgetItem(f"{price:.2f}"))
            self.cart_table.setItem(row, 3, QTableWidgetItem(f"{quantity * price:.2f}"))
            self.cart_table.setItem(row, 4, QTableWidgetItem(str(product_id)))

        self.update_total()

    def remove_from_cart(self) -> None:
        row = self.cart_table.currentRow()
        if row < 0:
            QMessageBox.warning(
                self, "Внимание", "Выберите товар в корзине для удаления"
            )
            return
        self.cart_table.removeRow(row)
        self.update_total()

    def update_total(self) -> None:
        total = 0.0
        for row in range(self.cart_table.rowCount()):
            item = self.cart_table.item(row, 3)
            if item is not None:
                try:
                    total += float(item.text())
                except ValueError:
                    pass

        if self.cart_table.rowCount() == 0:
            self.total_label.setText("Итого: 0 ₽")
        else:
            self.total_label.setText(f"Итого: {total:.0f} ₽")

    def confirm_order(self) -> None:
        if self.cart_table.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Корзина пуста")
            return

        QMessageBox.information(
            self, "Оформление заказа",
            "Корзина заполнена.\n"
            "Сохранение заказа в БД будет реализовано на следующей паре (ПТ 21).",
        )