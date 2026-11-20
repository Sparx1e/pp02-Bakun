from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton,
    QMessageBox, QSpinBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from resource_utils import resource_path

def load_product_pixmap(image_path, fallback="images/picture.png"):
    pixmap = QPixmap(str(resource_path(image_path))) if image_path else QPixmap()
    if pixmap.isNull():
        pixmap = QPixmap(str(resource_path(fallback)))
    if pixmap.isNull():
        pixmap = QPixmap(160, 120)
        pixmap.fill(Qt.GlobalColor.lightGray)
    return pixmap

class ProductCard(QDialog):
    def __init__(self, product_id, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.db = parent.db if parent is not None else None
        self.setWindowTitle("Карточка товара — Мир киберспорта")
        self.resize(300, 450)
        self.setup_ui()
        self.load_product(product_id)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.image_label = QLabel()
        self.image_label.setPixmap(load_product_pixmap(None))
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_label = QLabel("Загрузка...")
        self.name_label.setStyleSheet("font-weight: bold; font-size: 16px;")

        self.price_label = QLabel("Цена: ...")
        self.description_label = QLabel("Описание: ...")

        self.size_combo = QComboBox()
        self.size_combo.addItems(["Чёрный", "Белый", "Красный"])
        self.variant_combo = self.size_combo

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(10)

        self.add_button = QPushButton("В корзину")
        self.add_button.clicked.connect(self.add_selected_to_cart)

        for widget in (self.image_label, self.name_label, self.price_label,
                       self.description_label, self.size_combo,
                       self.quantity_spin, self.add_button):
            layout.addWidget(widget)

    def load_product(self, product_id):
        """Загружает данные о товаре из БД и заполняет виджеты."""
        if not self.db:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return

        try:
            self.db.cursor.execute("""
                SELECT p.name, p.price, p.description, p.image_path,
                       COALESCE(SUM(si.quantity), 0) AS total_quantity
                FROM products p
                LEFT JOIN stock_items si ON p.product_id = si.product_id
                WHERE p.product_id = %s
                GROUP BY p.product_id
            """, (product_id,))
            product = self.db.cursor.fetchone()

            if product is None:
                QMessageBox.critical(self, "Ошибка", "Товар не найден")
                self.reject()
                return

            name, price, description, image_path, total_quantity = product

            self.name_label.setText(name)
            self.price_label.setText(f"Цена: {price} руб.")
            self.description_label.setText(description or "Описание отсутствует")

            pixmap = load_product_pixmap(image_path)
            self.image_label.setPixmap(
                pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation) # type: ignore
            )

            self.quantity_spin.setMaximum(int(total_quantity))

            if total_quantity == 0:
                self.add_button.setEnabled(False)
                self.add_button.setText("Нет в наличии")
            else:
                self.add_button.setEnabled(True)
                self.add_button.setText("В корзину")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка при загрузке товара: {e}")

    def add_selected_to_cart(self):
        QMessageBox.information(
            self, "Этап разработки", "Корзина будет подключена в РТ 19"
        )