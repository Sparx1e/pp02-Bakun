from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox
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
        self.resize(300, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.image_label = QLabel()
        self.image_label.setPixmap(load_product_pixmap(None))
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_label = QLabel(f"Товар ID {self.product_id}")
        self.name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        self.price_label = QLabel("Цена: данные загрузятся в РТ 17")
        self.description_label = QLabel("Описание: данные загрузятся в РТ 17")

        self.size_combo = QComboBox()
        self.size_combo.addItems(["Чёрный", "Белый", "Красный"])
        self.variant_combo = self.size_combo

        self.add_button = QPushButton("В корзину")
        self.add_button.clicked.connect(self.add_selected_to_cart)

        for widget in (self.image_label, self.name_label, self.price_label,
                       self.description_label, self.size_combo, self.add_button):
            layout.addWidget(widget)

    def add_selected_to_cart(self):
        QMessageBox.information(
            self, "Этап разработки", "Корзина будет подключена в РТ 19"
        )