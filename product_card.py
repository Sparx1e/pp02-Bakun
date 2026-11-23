from pathlib import Path
import shutil
import uuid

import psycopg
from PySide6.QtCore import QStandardPaths, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox, QDialog, QFileDialog, QLabel, QMessageBox,
    QPushButton, QSpinBox, QVBoxLayout,
)

from resource_utils import resource_path


def load_product_pixmap(
    image_path, fallback: str = "images/picture.png"
) -> QPixmap:
    pixmap = QPixmap(str(resource_path(image_path))) if image_path else QPixmap()
    if pixmap.isNull():
        pixmap = QPixmap(str(resource_path(fallback)))
    if pixmap.isNull():
        pixmap = QPixmap(160, 120)
        pixmap.fill(Qt.GlobalColor.lightGray)
    return pixmap

def delete_product(self) -> None:
    """Удаление товара из БД с подтверждением и обработкой FK."""
    reply = QMessageBox.question(
        self,
        "Удаление товара",
        f"Вы уверены, что хотите удалить «{self.name_label.text()}»?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    if reply != QMessageBox.StandardButton.Yes:
        return

    if not self.db or not self.db.connection:
        QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
        return

    try:
        with self.db.connection.cursor() as cur:
            cur.execute(
                "DELETE FROM stock_items WHERE product_id = %s",
                (self.product_id,),
            )
            cur.execute(
                "DELETE FROM products WHERE product_id = %s",
                (self.product_id,),
            )
            if cur.rowcount == 0:
                raise ValueError("Товар не найден")

        self.db.connection.commit()
        QMessageBox.information(self, "Успех", "Товар удалён")

        if self.main_window is not None:
            self.main_window.load_products()

        self.accept()

    except psycopg.errors.ForeignKeyViolation:
        self.db.connection.rollback()
        QMessageBox.critical(
            self,
            "Ошибка",
            "Товар нельзя удалить: он есть в заказах",
        )
    except Exception as e:
        self.db.connection.rollback()
        QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}")

class ProductCard(QDialog):
    def __init__(self, product_id: int, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.main_window = parent
        self.db = parent.db if parent is not None else None
        self.base_price: float = 0.0
        self.current_price: float = 0.0
        self.stock_map: dict[str, tuple[int, float]] = {}

        self.setWindowTitle("Карточка товара — Мир киберспорта")
        self.resize(320, 560)
        self.setup_ui()
        self.load_product(product_id)

    def setup_ui(self) -> None:
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
        self.description_label.setWordWrap(True)

        self.variant_combo = QComboBox()
        self.variant_combo.currentTextChanged.connect(self.on_variant_changed)

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
            self.variant_combo,
            self.quantity_spin,
            self.add_button,
            self.delete_button,
            ):
            layout.addWidget(widget)

    def load_product(self, product_id: int) -> None:
        if not self.db:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return

        try:
            product = self.db.fetch_product(product_id)
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка БД", f"Ошибка при загрузке товара: {e}"
            )
            return

        if product is None:
            QMessageBox.critical(self, "Ошибка", "Товар не найден")
            self.reject()
            return

        name, price, description, image_path = product
        self.base_price = float(price)
        self.current_price = float(price)

        self.name_label.setText(name)
        self.price_label.setText(f"Цена: {price} руб.")
        self.description_label.setText(description or "Описание отсутствует")

        pixmap = load_product_pixmap(image_path)
        self.image_label.setPixmap(
            pixmap.scaled(
                200, 200,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

        try:
            stock = self.db.fetch_product_stock(product_id)
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка БД", f"Ошибка загрузки вариантов: {e}"
            )
            stock = []

        self.variant_combo.blockSignals(True)
        self.variant_combo.clear()
        self.stock_map.clear()
        for variant, qty, vprice in stock:
            self.variant_combo.addItem(variant)
            self.stock_map[variant] = (int(qty), float(vprice))
        self.variant_combo.blockSignals(False)

        if self.variant_combo.count() > 0:
            self.on_variant_changed(self.variant_combo.currentText())
        else:
            self.add_button.setEnabled(False)
            self.add_button.setText("Нет в наличии")
            self.quantity_spin.setEnabled(False)
            self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_product)

    def on_variant_changed(self, variant: str) -> None:
        qty, vprice = self.stock_map.get(variant, (0, self.base_price))
        self.current_price = vprice
        self.price_label.setText(f"Цена: {vprice:.0f} руб.")

        self.quantity_spin.setMaximum(max(qty, 1))
        self.quantity_spin.setEnabled(qty > 0)
        self.add_button.setEnabled(qty > 0)
        self.add_button.setText("В корзину" if qty > 0 else "Нет в наличии")

    def load_image(self) -> None:
        if not self.db or not self.db.connection:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение для товара",
            "",
            "Images (*.png *.jpg *.jpeg)",
        )
        if not file_path:
            return

        if QPixmap(file_path).isNull():
            QMessageBox.warning(
                self, "Изображение", "Файл не является изображением"
            )
            return

        base = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppLocalDataLocation
        )
        if not base:
            QMessageBox.critical(
                self, "Ошибка",
                "Не удалось определить каталог для сохранения изображений",
            )
            return

        target = Path(base) / "images" / (uuid.uuid4().hex + Path(file_path).suffix)

        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, target)
            self.db.update_product_image(self.product_id, str(target))
        except (OSError, psycopg.Error, ValueError) as error:
            if self.db.connection:
                self.db.connection.rollback()
            if target.exists():
                target.unlink()
            QMessageBox.critical(self, "Изображение не сохранено", str(error))
            return

        pixmap = QPixmap(str(target))
        self.image_label.setPixmap(
            pixmap.scaled(
                200, 200,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
        QMessageBox.information(self, "Готово", "Изображение товара обновлено")

    def add_selected_to_cart(self) -> None:
        if self.main_window is None:
            QMessageBox.critical(self, "Ошибка", "Нет ссылки на главное окно")
            return

        variant = self.variant_combo.currentText().strip()
        quantity = self.quantity_spin.value()
        name = self.name_label.text()
        price = self.current_price
        product_id = self.product_id

        display_name = f"{name} ({variant})" if variant else name

        try:
            self.main_window.add_to_cart(
                display_name, quantity, price, product_id
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось добавить товар: {e}"
            )
            return

        QMessageBox.information(
            self, "Корзина",
            f"«{display_name}» × {quantity} добавлен в корзину",
        )
    delete_product = None