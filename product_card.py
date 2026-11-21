from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton,
    QMessageBox, QSpinBox, QFileDialog
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QStandardPaths
import shutil
import uuid
from pathlib import Path
import psycopg
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
        self.resize(300, 500)
        self.setup_ui()
        self.load_product(product_id)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.image_label = QLabel()
        self.image_label.setPixmap(load_product_pixmap(None))
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.load_image_button = QPushButton("Загрузить изображение")
        self.load_image_button.clicked.connect(self.load_image)

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

        for widget in (
            self.image_label,
            self.load_image_button,
            self.name_label,
            self.price_label,
            self.description_label,
            self.size_combo,
            self.quantity_spin,
            self.add_button,
        ):
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

    def load_image(self):
        """Выбор, копирование изображения и обновление пути в БД."""
        if not self.db or not self.db.connection:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение для товара",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )
        if not file_path:
            return

        if QPixmap(file_path).isNull():
            QMessageBox.warning(self, "Изображение", "Файл не является изображением")
            return

        base = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppLocalDataLocation
        )
        if not base:
            QMessageBox.critical(
                self,
                "Ошибка",
                "Не удалось определить каталог для сохранения изображений"
            )
            return

        target = Path(base) / "images" / (
            uuid.uuid4().hex + Path(file_path).suffix
        )

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, target)

            with self.db.connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE products SET image_path = %s WHERE product_id = %s",
                    (str(target), self.product_id)
                )
                if cursor.rowcount != 1:
                    raise ValueError("Товар не найден")

            self.db.connection.commit()

        except (OSError, psycopg.Error, ValueError) as error:
            self.db.connection.rollback()
            if target.exists():
                target.unlink()
            QMessageBox.critical(
                self,
                "Изображение не сохранено",
                str(error)
            )
            return

        pixmap = QPixmap(str(target))
        self.image_label.setPixmap(
            pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation) # type: ignore
        )
        QMessageBox.information(self, "Готово", "Изображение товара обновлено")

    def add_selected_to_cart(self):
        QMessageBox.information(
            self, "Этап разработки", "Корзина будет подключена в РТ 19"
        )