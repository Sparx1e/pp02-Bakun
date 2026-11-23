import psycopg
class Database:
    """Тонкая обёртка над psycopg3 с удобными методами запросов."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        dbname: str = "esports_shop",
        user: str = "postgres",
        password: str = "123",
    ):
        self.connection: psycopg.Connection | None = None
        self.cursor: psycopg.Cursor | None = None
        self._params = dict(
            host=host, port=port, dbname=dbname, user=user, password=password
        )

    def connect(self) -> bool:
        try:
            self.connection = psycopg.connect(**self._params) # type: ignore
            self.cursor = self.connection.cursor()
            print("Подключение к PostgreSQL успешно")
            return True
        except psycopg.Error as e:
            print(f"Ошибка подключения: {e}")
            return False

    def close(self) -> None:
        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def fetch_user_by_login(self, login: str):
        """Возвращает (user_id, role_id, last_name, first_name, middle_name)."""
        assert self.cursor is not None
        self.cursor.execute(
            """
            SELECT user_id, role_id, last_name, first_name, middle_name
            FROM users
            WHERE login = %s
            """,
            (login,),
        )
        return self.cursor.fetchone()

    def fetch_categories(self) -> list[str]:
        assert self.cursor is not None
        self.cursor.execute(
            "SELECT DISTINCT category FROM products ORDER BY category"
        )
        return [row[0] for row in self.cursor.fetchall()]

    def fetch_products(
        self,
        search: str = "",
        category: str = "Все категории",
        sort: str = "По возрастанию",
    ):
        """Возвращает (product_id, name, description, price)."""
        query = """
            SELECT product_id, name, COALESCE(description, ''), price
            FROM products
            WHERE (name ILIKE %s OR COALESCE(description, '') ILIKE %s)
        """
        params: list = [f"%{search}%", f"%{search}%"]
        if category and category != "Все категории":
            query += " AND category = %s"
            params.append(category)
        query += (
            " ORDER BY price ASC, product_id ASC"
            if sort == "По возрастанию"
            else " ORDER BY price DESC, product_id ASC"
        )
        assert self.cursor is not None
        self.cursor.execute(query, tuple(params))
        return self.cursor.fetchall()

    def fetch_product(self, product_id: int):
        """Возвращает (name, price, description, image_path)."""
        assert self.cursor is not None
        self.cursor.execute(
            """
            SELECT name, price, COALESCE(description, ''), image_path
            FROM products
            WHERE product_id = %s
            """,
            (product_id,),
        )
        return self.cursor.fetchone()

    def fetch_product_stock(self, product_id: int):
        """Возвращает список (variant, quantity, price) из stock_items."""
        assert self.cursor is not None
        self.cursor.execute(
            """
            SELECT variant, quantity, price
            FROM stock_items
            WHERE product_id = %s
            ORDER BY variant
            """,
            (product_id,),
        )
        return self.cursor.fetchall()

    def update_product_image(self, product_id: int, image_path: str) -> None:
        assert self.connection is not None
        with self.connection.cursor() as cur:
            cur.execute(
                "UPDATE products SET image_path = %s WHERE product_id = %s",
                (image_path, product_id),
            )
            if cur.rowcount != 1:
                raise ValueError("Товар не найден")
        self.connection.commit()

    def fetch_orders(self):
        """Возвращает список заказов: (order_id, order_date, full_name, total, status)."""
        assert self.cursor is not None
        self.cursor.execute(
            """
            SELECT
                o.order_id,
                o.order_date,
                COALESCE(
                    NULLIF(CONCAT_WS(' ', u.last_name, u.first_name, u.middle_name), ''),
                    'Пользователь удалён'
                ) AS full_name,
                COALESCE(SUM(oi.quantity * oi.price), 0) AS total,
                COALESCE(o.status, 'Новый') AS status
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.user_id
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            GROUP BY
                o.order_id,
                o.order_date,
                u.last_name,
                u.first_name,
                u.middle_name,
                o.status
            ORDER BY o.order_date DESC, o.order_id DESC
            """
        )
        return self.cursor.fetchall()