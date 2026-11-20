import psycopg

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = psycopg.connect(
                host="localhost",
                port=5432,
                dbname="esports_shop",
                user="postgres",
                password="123"
            )
            self.cursor = self.connection.cursor()
            print("Подключение к PostgreSQL успешно")
            return True
        except psycopg.Error as e:
            print(f"Ошибка подключения: {e}")
            return False