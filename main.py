from datetime import date
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox, QDialog, QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMessageBox, QPushButton, QSpinBox, QStackedWidget,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)
from product_card import ProductCard

PAGE_CATALOG, PAGE_CART, PAGE_ORDERS = 0, 1, 2
COL_NAME, COL_QUANTITY, COL_PRICE, COL_SUM, COL_PRODUCT_ID, COL_VARIANT = range(6)
CAT_COL_ID, CAT_COL_NAME, CAT_COL_DESC, CAT_COL_PRICE = range(4)


class MainWindow(QMainWindow):
    def __init__(self, db, user_id=None, role_id=None, role_name=None, full_name=None):
        super().__init__()
        self.db = db
        self.user_id = user_id
        self.role_id = role_id
        self.role_name = role_name or "Гость"
        self.full_name = full_name or "Гость"
        self.setWindowTitle("Мир киберспорта")
        self.resize(960, 680)
        self.setup_ui()
        self.setup_role_interface()
        self.load_products()

    def setup_ui(self):
        cw = QWidget(); self.setCentralWidget(cw)
        ml = QVBoxLayout(cw)
        t = QLabel("Мир киберспорта")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t.setStyleSheet("font-size: 24px; font-weight: bold; color: #458B8B;")
        ml.addWidget(t)
        ml.addWidget(QLabel(f"Вы вошли как: {self.full_name} ({self.role_name})"))
        self.stacked_widget = QStackedWidget(); ml.addWidget(self.stacked_widget, 1)
        self._build_catalog_page()
        self._build_cart_page()
        self._build_orders_page()
        back = QPushButton("← Назад в каталог"); back.clicked.connect(self.go_back)
        ml.addWidget(back)
        self.switch_page(PAGE_CATALOG)

    def _build_catalog_page(self):
        self.catalog_page = QWidget(); l = QVBoxLayout(self.catalog_page)
        fl = QHBoxLayout()
        self.search_input = QLineEdit(); self.search_input.setPlaceholderText("Поиск...")
        self.search_input.textChanged.connect(self.load_products)
        self.category_combo = QComboBox(); self.category_combo.addItem("Все категории")
        self.category_combo.currentIndexChanged.connect(self.load_products)
        self._load_categories_into_combo()
        self.sort_combo = QComboBox(); self.sort_combo.addItems(["По возрастанию", "По убыванию"])
        self.sort_combo.currentIndexChanged.connect(self.load_products)
        fl.addWidget(self.search_input, 1); fl.addWidget(self.category_combo)
        fl.addWidget(QLabel("Сортировка:")); fl.addWidget(self.sort_combo)
        l.addLayout(fl)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Наименование", "Описание", "Цена"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.doubleClicked.connect(self.open_selected_product_card)
        l.addWidget(self.table, 1)
        b1 = QPushButton("Открыть карточку"); b1.clicked.connect(self.open_selected_product_card)
        b2 = QPushButton("В корзину"); b2.clicked.connect(lambda: self.switch_page(PAGE_CART))
        b3 = QPushButton("К заказам"); b3.clicked.connect(lambda: self.switch_page(PAGE_ORDERS))
        l.addWidget(b1); l.addWidget(b2); l.addWidget(b3)
        self.stacked_widget.addWidget(self.catalog_page)

    def _build_cart_page(self):
        self.cart_page = QWidget(); l = QVBoxLayout(self.cart_page)
        l.addWidget(QLabel("Корзина"))
        self.cart_table = QTableWidget(0, 6)
        self.cart_table.setHorizontalHeaderLabels(
            ["Наименование", "Кол-во", "Цена", "Сумма", "ID", "Вариант"])
        self.cart_table.setColumnHidden(COL_PRODUCT_ID, True)
        self.cart_table.setColumnHidden(COL_VARIANT, True)
        self.cart_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.cart_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        l.addWidget(self.cart_table, 1)
        self.total_label = QLabel("Итого: 0 ₽"); self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        l.addWidget(self.total_label)
        self.remove_button = QPushButton("Удалить"); self.remove_button.clicked.connect(self.remove_from_cart)
        self.confirm_button = QPushButton("Оформить"); self.confirm_button.clicked.connect(self.confirm_order)
        l.addWidget(self.remove_button); l.addWidget(self.confirm_button)
        self.stacked_widget.addWidget(self.cart_page)

    def _build_orders_page(self):
        self.orders_page = QWidget(); l = QVBoxLayout(self.orders_page)
        l.addWidget(QLabel("Заказы"))
        self.orders_table = QTableWidget(0, 4)
        self.orders_table.setHorizontalHeaderLabels(["Дата", "Клиент", "Сумма", "Статус"])
        self.orders_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.orders_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        l.addWidget(self.orders_table, 1)
        self.btn_add_order = QPushButton("Добавить заказ"); self.btn_add_order.clicked.connect(self.open_add_order_dialog)
        self.btn_delete_order = QPushButton("Удалить заказ"); self.btn_delete_order.clicked.connect(self.delete_selected_order)
        self.btn_edit_order = QPushButton("Редактировать заказ")
        self.btn_refresh_orders = QPushButton("Обновить"); self.btn_refresh_orders.clicked.connect(self.load_orders)
        l.addWidget(self.btn_refresh_orders); l.addWidget(self.btn_add_order)
        l.addWidget(self.btn_delete_order); l.addWidget(self.btn_edit_order)
        self.stacked_widget.addWidget(self.orders_page)

    def setup_role_interface(self):
        if self.role_id == 1:
            self.btn_add_order.show(); self.btn_delete_order.show(); self.btn_edit_order.show()
        elif self.role_id == 2:
            self.btn_add_order.show(); self.btn_delete_order.show(); self.btn_edit_order.hide()
        else:
            self.btn_add_order.hide(); self.btn_delete_order.hide(); self.btn_edit_order.hide()

    def go_back(self):
        if self.stacked_widget.currentIndex() != PAGE_CATALOG:
            self.switch_page(PAGE_CATALOG)

    def switch_page(self, index):
        self.stacked_widget.setCurrentIndex(index)
        self.setWindowTitle(["Мир киберспорта — Каталог", "Мир киберспорта — Корзина",
                             "Мир киберспорта — Заказы"][index])
        if index == PAGE_CATALOG:
            self.load_products()
        elif index == PAGE_CART:
            self.update_total()
        elif index == PAGE_ORDERS:
            self.load_orders()

    def _load_categories_into_combo(self):
        try:
            cats = self.db.fetch_categories()
        except Exception:
            cats = []
        self.category_combo.blockSignals(True)
        for c in cats:
            self.category_combo.addItem(c)
        self.category_combo.blockSignals(False)

    def load_products(self, *_):
        search = self.search_input.text().strip()
        cat = self.category_combo.currentText()
        sort = self.sort_combo.currentText()
        try:
            products = self.db.fetch_products(search, cat, sort)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e)); return
        self.table.setRowCount(0); self.table.setRowCount(len(products))
        for r, (pid, name, desc, price) in enumerate(products):
            self.table.setItem(r, CAT_COL_ID, QTableWidgetItem(str(pid)))
            self.table.setItem(r, CAT_COL_NAME, QTableWidgetItem(name))
            self.table.setItem(r, CAT_COL_DESC, QTableWidgetItem(desc))
            self.table.setItem(r, CAT_COL_PRICE, QTableWidgetItem(str(price)))

    def open_selected_product_card(self, *_):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите товар"); return
        item = self.table.item(row, CAT_COL_ID)
        if item is None: return
        ProductCard(int(item.text()), self.role_id, self).exec()

    def add_to_cart(self, name, variant, quantity, price, product_id):
        quantity = int(quantity); price = float(price)
        if quantity <= 0:
            QMessageBox.warning(self, "Корзина", "Кол-во > 0"); return
        for row in range(self.cart_table.rowCount()):
            pid_item = self.cart_table.item(row, COL_PRODUCT_ID)
            var_item = self.cart_table.item(row, COL_VARIANT)
            if pid_item and var_item and pid_item.text() == str(product_id) and var_item.text() == (variant or ""):
                old_qty = int(self.cart_table.item(row, COL_QUANTITY).text()) # type: ignore
                new_qty = old_qty + quantity
                self.cart_table.setItem(row, COL_QUANTITY, QTableWidgetItem(str(new_qty)))
                self.cart_table.setItem(row, COL_SUM, QTableWidgetItem(f"{new_qty * price:.2f}"))
                self.update_total(); return
        r = self.cart_table.rowCount(); self.cart_table.insertRow(r)
        display = f"{name} ({variant})" if variant else name
        self.cart_table.setItem(r, COL_NAME, QTableWidgetItem(display))
        self.cart_table.setItem(r, COL_QUANTITY, QTableWidgetItem(str(quantity)))
        self.cart_table.setItem(r, COL_PRICE, QTableWidgetItem(f"{price:.2f}"))
        self.cart_table.setItem(r, COL_SUM, QTableWidgetItem(f"{quantity * price:.2f}"))
        self.cart_table.setItem(r, COL_PRODUCT_ID, QTableWidgetItem(str(product_id)))
        self.cart_table.setItem(r, COL_VARIANT, QTableWidgetItem(variant or ""))
        self.update_total()

    def remove_from_cart(self):
        row = self.cart_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите строку"); return
        self.cart_table.removeRow(row); self.update_total()

    def update_total(self):
        total = 0.0
        for r in range(self.cart_table.rowCount()):
            item = self.cart_table.item(r, COL_SUM)
            if item:
                try: total += float(item.text())
                except ValueError: pass
        self.total_label.setText(f"Итого: {total:.0f} ₽")

    def confirm_order(self):
        if self.cart_table.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Корзина пуста"); return
        if self.user_id is None:
            QMessageBox.critical(self, "Ошибка", "Нет авторизации"); return
        cursor = self.db.cursor
        try:
            cursor.execute(
                "INSERT INTO orders (order_date, user_id, status) VALUES (%s, %s, %s) RETURNING order_id",
                (date.today(), self.user_id, "Новый"),
            )
            order_id = cursor.fetchone()[0]
            for r in range(self.cart_table.rowCount()):
                pid = int(self.cart_table.item(r, COL_PRODUCT_ID).text()) # type: ignore
                var = self.cart_table.item(r, COL_VARIANT).text() # type: ignore
                qty = int(self.cart_table.item(r, COL_QUANTITY).text()) # type: ignore
                price = float(self.cart_table.item(r, COL_PRICE).text()) # type: ignore
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, variant, quantity, price) VALUES (%s,%s,%s,%s,%s)",
                    (order_id, pid, var, qty, price),
                )
                cursor.execute(
                    "UPDATE stock_items SET quantity = quantity - %s WHERE product_id = %s AND variant = %s",
                    (qty, pid, var),
                )
            self.db.connection.commit()
            QMessageBox.information(self, "Успех", f"Заказ №{order_id} оформлен")
            self.cart_table.setRowCount(0); self.update_total()
        except Exception as e:
            self.db.connection.rollback()
            QMessageBox.critical(self, "Ошибка", str(e))

    def open_add_order_dialog(self):
        AddOrderDialog(self.db, self).exec()
        self.load_orders()

    def delete_selected_order(self):
        row = self.orders_table.currentRow()
        if row < 0: return
        item = self.orders_table.item(row, 0)
        order_id = item.data(Qt.ItemDataRole.UserRole) if item else None
        if order_id is None: return
        if QMessageBox.question(self, "Удаление", f"Удалить заказ №{order_id}?") != QMessageBox.StandardButton.Yes:
            return
        try:
            self.db.cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
            self.db.cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
            self.db.connection.commit(); self.load_orders()
        except Exception as e:
            self.db.connection.rollback(); QMessageBox.critical(self, "Ошибка", str(e))

    def load_orders(self):
        try:
            orders = self.db.fetch_orders()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e)); return
        self.orders_table.setRowCount(0); self.orders_table.setRowCount(len(orders))
        for r, (oid, odate, fio, total, status) in enumerate(orders):
            it = QTableWidgetItem(str(odate)); it.setData(Qt.ItemDataRole.UserRole, oid)
            self.orders_table.setItem(r, 0, it)
            self.orders_table.setItem(r, 1, QTableWidgetItem(str(fio)))
            self.orders_table.setItem(r, 2, QTableWidgetItem(f"{float(total):.2f} ₽"))
            self.orders_table.setItem(r, 3, QTableWidgetItem(str(status)))


class AddOrderDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db; self.order_id = None; self.selected_product_id = None
        self.stock_map = {}
        self.setWindowTitle("Добавить заказ")
        self.resize(700, 620)
        self._build(); self.load_products()

    def _build(self):
        l = QVBoxLayout(self)
        l.addWidget(QLabel("Клиент:"))
        self.client_combo = QComboBox()
        for uid, fio in self.db.fetch_clients():
            self.client_combo.addItem(fio, uid)
        l.addWidget(self.client_combo)
        l.addWidget(QLabel("Статус:"))
        self.status_combo = QComboBox(); self.status_combo.addItems(["Новый", "В обработке", "Завершён"])
        l.addWidget(self.status_combo)
        b = QPushButton("Сохранить заказ"); b.clicked.connect(self.save_order); l.addWidget(b)
        self.info = QLabel("Заказ не создан"); l.addWidget(self.info)
        l.addWidget(QLabel("Поиск:"))
        self.search_input = QLineEdit(); self.search_input.setPlaceholderText("Например: Мышь")
        self.search_input.textChanged.connect(self.load_products); l.addWidget(self.search_input)
        self.product_table = QTableWidget(0, 3)
        self.product_table.setHorizontalHeaderLabels(["ID", "Товар", "Цена"])
        self.product_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.product_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.product_table.cellClicked.connect(self.on_product_selected)
        l.addWidget(self.product_table, 1)
        l.addWidget(QLabel("Вариант:"))
        self.variant_combo = QComboBox(); self.variant_combo.currentIndexChanged.connect(self.update_qty_limit)
        l.addWidget(self.variant_combo)
        l.addWidget(QLabel("Количество:"))
        self.quantity_spin = QSpinBox(); self.quantity_spin.setMinimum(1); self.quantity_spin.setMaximum(1)
        l.addWidget(self.quantity_spin)
        self.add_item_button = QPushButton("Добавить в заказ")
        self.add_item_button.clicked.connect(self.add_item_to_order)
        self.add_item_button.setEnabled(False); l.addWidget(self.add_item_button)
        c = QPushButton("Закрыть"); c.clicked.connect(self.accept); l.addWidget(c)

    def load_products(self, *_):
        search = self.search_input.text().strip()
        self.db.cursor.execute(
            "SELECT product_id, name, price FROM products WHERE name ILIKE %s ORDER BY name",
            (f"%{search}%",),
        )
        rows = self.db.cursor.fetchall()
        self.product_table.setRowCount(0); self.product_table.setRowCount(len(rows))
        for r, (pid, name, price) in enumerate(rows):
            it = QTableWidgetItem(str(pid)); it.setData(Qt.ItemDataRole.UserRole, pid)
            self.product_table.setItem(r, 0, it)
            self.product_table.setItem(r, 1, QTableWidgetItem(name))
            self.product_table.setItem(r, 2, QTableWidgetItem(str(price)))
        self.selected_product_id = None
        self.variant_combo.clear()
        self.quantity_spin.setMaximum(1)
        self.add_item_button.setEnabled(False)
        self.add_item_button.setText("Добавить в заказ")

    def save_order(self):
        if self.order_id is not None:
            QMessageBox.information(self, "Инфо", f"Заказ №{self.order_id} уже создан")
            return
        try:
            uid = self.client_combo.currentData()
            if uid is None: raise ValueError("Не выбран клиент")
            self.db.cursor.execute(
                "INSERT INTO orders (order_date, user_id, status) VALUES (%s,%s,%s) RETURNING order_id",
                (date.today(), uid, self.status_combo.currentText()),
            )
            self.order_id = self.db.cursor.fetchone()[0]
            self.db.connection.commit()
            self.info.setText(f"Заказ №{self.order_id} создан")
            QMessageBox.information(self, "Успех", f"Заказ №{self.order_id} создан")
        except Exception as e:
            self.db.connection.rollback(); QMessageBox.critical(self, "Ошибка", str(e))

    def on_product_selected(self, row, _col=0):
        item = self.product_table.item(row, 0)
        if item is None: return
        self.selected_product_id = int(item.data(Qt.ItemDataRole.UserRole) or item.text())
        self.db.cursor.execute(
            "SELECT variant, quantity, price FROM stock_items WHERE product_id = %s ORDER BY variant",
            (self.selected_product_id,),
        )
        rows = self.db.cursor.fetchall()
        self.variant_combo.blockSignals(True); self.variant_combo.clear(); self.stock_map.clear()
        for var, qty, price in rows:
            self.variant_combo.addItem(f"{var} (остаток: {qty})", var)
            self.stock_map[var] = (int(qty), float(price))
        self.variant_combo.blockSignals(False)
        if self.variant_combo.count() > 0:
            self.update_qty_limit()
        else:
            self.add_item_button.setEnabled(False); self.add_item_button.setText("Нет в наличии")

    def update_qty_limit(self):
        if self.selected_product_id is None or self.variant_combo.count() == 0:
            self.add_item_button.setEnabled(False); return
        var = self.variant_combo.currentData()
        qty, price = self.stock_map.get(var, (0, 0.0))
        self.quantity_spin.setMaximum(max(qty, 1))
        self.add_item_button.setEnabled(qty > 0)
        self.add_item_button.setText(
            f"Добавить ({price:.0f} руб.)" if qty > 0 else "Нет в наличии")

    def add_item_to_order(self):
        if self.order_id is None:
            QMessageBox.warning(self, "Ошибка", "Сначала сохраните заказ"); return
        if self.selected_product_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите товар"); return
        var = self.variant_combo.currentData()
        if not var:
            QMessageBox.warning(self, "Ошибка", "Выберите вариант"); return
        qty = self.quantity_spin.value()
        try:
            self.db.cursor.execute(
                "SELECT quantity, price FROM stock_items WHERE product_id = %s AND variant = %s",
                (self.selected_product_id, var),
            )
            row = self.db.cursor.fetchone()
            if row is None: raise ValueError("Вариант не найден")
            stock, price = int(row[0]), float(row[1])
            if qty > stock: raise ValueError(f"На складе только {stock} шт.")
            self.db.cursor.execute(
                "INSERT INTO order_items (order_id, product_id, variant, quantity, price) VALUES (%s,%s,%s,%s,%s)",
                (self.order_id, self.selected_product_id, var, qty, price),
            )
            self.db.cursor.execute(
                "UPDATE stock_items SET quantity = quantity - %s WHERE product_id = %s AND variant = %s",
                (qty, self.selected_product_id, var),
            )
            self.db.connection.commit()
            QMessageBox.information(self, "Успех", "Товар добавлен в заказ")
            self.load_products()
        except Exception as e:
            self.db.connection.rollback(); QMessageBox.critical(self, "Ошибка", str(e))