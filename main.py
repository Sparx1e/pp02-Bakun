from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPushButton, QSpinBox, QStackedWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)
from product_card import ProductCard
from datetime import date

PAGE_CATALOG = 0
PAGE_CART = 1
PAGE_ORDERS = 2

COL_NAME = 0
COL_QUANTITY = 1
COL_PRICE = 2
COL_SUM = 3
COL_PRODUCT_ID = 4

CAT_COL_ID = 0
CAT_COL_NAME = 1
CAT_COL_DESC = 2
CAT_COL_PRICE = 3


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
        self.resize(960, 680)

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

        user_info_label = QLabel(
            f"Вы вошли как: {self.full_name} ({self.role_name})"
        )
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
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.doubleClicked.connect(self.open_selected_product_card)
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
        self.cart_table.setColumnHidden(COL_PRODUCT_ID, True)
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

        change_row = QHBoxLayout()
        self.change_quantity_spin = QSpinBox()
        self.change_quantity_spin.setMinimum(1)
        self.change_quantity_spin.setMaximum(999)

        self.change_quantity_button = QPushButton("Изменить количество")
        self.change_quantity_button.clicked.connect(self.change_quantity)

        change_row.addWidget(QLabel("Новое количество:"))
        change_row.addWidget(self.change_quantity_spin)
        change_row.addWidget(self.change_quantity_button)
        change_row.addStretch(1)
        layout.addLayout(change_row)

        btn_row = QHBoxLayout()

        self.remove_button = QPushButton("Удалить выбранный товар")
        self.remove_button.clicked.connect(self.remove_from_cart)

        self.toggle_id_button = QPushButton("Показать / скрыть ID")
        self.toggle_id_button.clicked.connect(self.toggle_product_id_column)

        self.confirm_button = QPushButton("Оформить заказ")
        self.confirm_button.clicked.connect(self.confirm_order)

        btn_row.addWidget(self.remove_button)
        btn_row.addWidget(self.toggle_id_button)
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
            self.table.setItem(row_idx, CAT_COL_ID, QTableWidgetItem(str(pid)))
            self.table.setItem(row_idx, CAT_COL_NAME, QTableWidgetItem(name))
            self.table.setItem(row_idx, CAT_COL_DESC, QTableWidgetItem(description))
            self.table.setItem(row_idx, CAT_COL_PRICE, QTableWidgetItem(str(price)))

    def open_selected_product_card(self, *_) -> None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(
                self, "Внимание",
                "Выберите товар из списка (кликните по строке).",
            )
            return

        pid_item = self.table.item(row, CAT_COL_ID)
        if pid_item is None:
            return
        try:
            product_id = int(pid_item.text())
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Некорректный ID товара")
            return

        card = ProductCard(product_id, self)
        card.exec()

    def add_to_cart(
        self, name: str, quantity: int, price: float, product_id: int
    ) -> None:
        """Добавляет товар. Дубликат (name + product_id) увеличивает количество."""
        try:
            quantity = int(quantity)
            price = float(price)
        except (TypeError, ValueError) as e:
            QMessageBox.critical(self, "Ошибка корзины", f"Неверные данные: {e}")
            return

        if quantity <= 0:
            QMessageBox.warning(self, "Корзина", "Количество должно быть > 0")
            return

        existing_row = -1
        for row in range(self.cart_table.rowCount()):
            name_item = self.cart_table.item(row, COL_NAME)
            id_item = self.cart_table.item(row, COL_PRODUCT_ID)
            if (
                name_item is not None
                and id_item is not None
                and id_item.text() == str(product_id)
                and name_item.text() == name
            ):
                existing_row = row
                break

        if existing_row >= 0:
            old_qty_item = self.cart_table.item(existing_row, COL_QUANTITY)
            price_item = self.cart_table.item(existing_row, COL_PRICE)
            old_qty = int(old_qty_item.text()) if old_qty_item else 0
            stored_price = float(price_item.text()) if price_item else price
            new_qty = old_qty + quantity

            self.cart_table.setItem(
                existing_row, COL_QUANTITY, QTableWidgetItem(str(new_qty))
            )
            self.cart_table.setItem(
                existing_row, COL_SUM,
                QTableWidgetItem(f"{new_qty * stored_price:.2f}")
            )
        else:
            row = self.cart_table.rowCount()
            self.cart_table.insertRow(row)
            self.cart_table.setItem(row, COL_NAME, QTableWidgetItem(str(name)))
            self.cart_table.setItem(row, COL_QUANTITY, QTableWidgetItem(str(quantity)))
            self.cart_table.setItem(row, COL_PRICE, QTableWidgetItem(f"{price:.2f}"))
            self.cart_table.setItem(
                row, COL_SUM, QTableWidgetItem(f"{quantity * price:.2f}")
            )
            self.cart_table.setItem(
                row, COL_PRODUCT_ID, QTableWidgetItem(str(product_id))
            )

        self.update_total()

    def change_quantity(self) -> None:
        row = self.cart_table.currentRow()
        if row < 0:
            QMessageBox.warning(
                self, "Внимание",
                "Выберите товар в корзине, чтобы изменить количество",
            )
            return

        price_item = self.cart_table.item(row, COL_PRICE)
        if price_item is None:
            QMessageBox.critical(self, "Ошибка", "Не удалось прочитать цену товара")
            return
        try:
            price = float(price_item.text())
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Некорректная цена в корзине")
            return

        new_quantity = int(self.change_quantity_spin.value())

        self.cart_table.setItem(
            row, COL_QUANTITY, QTableWidgetItem(str(new_quantity))
        )
        self.cart_table.setItem(
            row, COL_SUM, QTableWidgetItem(f"{new_quantity * price:.2f}")
        )
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
            item = self.cart_table.item(row, COL_SUM)
            if item is None:
                continue
            try:
                total += float(item.text())
            except ValueError:
                continue

        if self.cart_table.rowCount() == 0:
            self.total_label.setText("Итого: 0 ₽")
        else:
            self.total_label.setText(f"Итого: {total:.0f} ₽")

    def toggle_product_id_column(self) -> None:
        current = self.cart_table.isColumnHidden(COL_PRODUCT_ID)
        self.cart_table.setColumnHidden(COL_PRODUCT_ID, not current)

    def confirm_order(self) -> None:
        if self.cart_table.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Корзина пуста")
            return

        if self.user_id is None:
            QMessageBox.critical(self, "Ошибка", "Пользователь не авторизован")
            return

        if self.db.cursor is None or self.db.connection is None:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return

        cursor = self.db.cursor

        try:
            cursor.execute(
                """
                INSERT INTO orders (order_date, user_id, status)
                VALUES (%s, %s, %s)
                RETURNING order_id
                """,
                (date.today(), self.user_id, "Новый"),
            )
            order_id = cursor.fetchone()[0]

            for row in range(self.cart_table.rowCount()):
                qty_item = self.cart_table.item(row, COL_QUANTITY)
                price_item = self.cart_table.item(row, COL_PRICE)
                pid_item = self.cart_table.item(row, COL_PRODUCT_ID)

                if qty_item is None or price_item is None or pid_item is None:
                    raise ValueError(
                        f"Некорректные данные в строке корзины {row + 1}"
                    )

                product_id = int(pid_item.text())
                quantity = int(qty_item.text())
                price = float(price_item.text())

                if quantity <= 0:
                    raise ValueError("Количество должно быть больше 0")

                cursor.execute(
                    """
                    INSERT INTO order_items
                        (order_id, product_id, quantity, price)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (order_id, product_id, quantity, price),
                )

            self.db.connection.commit()

            QMessageBox.information(
                self,
                "Успех",
                f"Заказ №{order_id} оформлен",
            )

            self.cart_table.setRowCount(0)
            self.update_total()

        except Exception as e:
            self.db.connection.rollback()
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Ошибка при сохранении заказа: {e}",
            )