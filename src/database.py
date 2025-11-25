"""
Moduł do zarządzania bazą danych SQLite
"""
import sqlite3
import csv
import os

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_default_db_path = os.path.join(_project_root, "database", "movies.db")
_csv_dir = os.path.join(_project_root, "database")


class Database:
    """Klasa do zarządzania bazą danych SQLite"""

    def __init__(self, db_path: str = _default_db_path):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Nawiązuje połączenie z bazą danych"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Zamyka połączenie z bazą danych"""
        if self.conn:
            self.conn.close()

    def create_schema(self):
        """Tworzy schemat bazy danych"""
        cursor = self.conn.cursor()

        # Tabela movies
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                movieId INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                genres TEXT
            )
        ''')

        # Tabela links
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                movieId INTEGER PRIMARY KEY,
                imdbId TEXT,
                tmdbId TEXT,
                FOREIGN KEY (movieId) REFERENCES movies(movieId)
            )
        ''')

        # Tabela ratings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userId INTEGER NOT NULL,
                movieId INTEGER NOT NULL,
                rating REAL NOT NULL,
                timestamp INTEGER NOT NULL,
                FOREIGN KEY (movieId) REFERENCES movies(movieId)
            )
        ''')

        # Indeks dla szybszego wyszukiwania
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_ratings_movie 
            ON ratings(movieId)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_ratings_user 
            ON ratings(userId)
        ''')

        # Tabela tags
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userId INTEGER NOT NULL,
                movieId INTEGER NOT NULL,
                tag TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                FOREIGN KEY (movieId) REFERENCES movies(movieId)
            )
        ''')

        # Indeks dla szybszego wyszukiwania
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tags_movie 
            ON tags(movieId)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tags_user 
            ON tags(userId)
        ''')

        self.conn.commit()
        print("Schemat bazy danych został utworzony.")

    def load_movies_from_csv(self, csv_path: str = os.path.join(_csv_dir, "movies.csv")):
        """Ładuje dane z pliku movies.csv do bazy danych"""
        cursor = self.conn.cursor()

        # Czyścimy tabelę przed załadowaniem
        cursor.execute("DELETE FROM movies")

        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                cursor.execute(
                    "INSERT INTO movies (movieId, title, genres) VALUES (?, ?, ?)",
                    (int(row['movieId']), row['title'], row['genres'])
                )

        self.conn.commit()
        count = cursor.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
        print(f"Załadowano {count} filmów.")

    def load_links_from_csv(self, csv_path: str = os.path.join(_csv_dir, "links.csv")):
        """Ładuje dane z pliku links.csv do bazy danych"""
        cursor = self.conn.cursor()

        # Czyścimy tabelę przed załadowaniem
        cursor.execute("DELETE FROM links")

        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                cursor.execute(
                    "INSERT INTO links (movieId, imdbId, tmdbId) VALUES (?, ?, ?)",
                    (int(row['movieId']), row['imdbId'], row['tmdbId'])
                )

        self.conn.commit()
        count = cursor.execute("SELECT COUNT(*) FROM links").fetchone()[0]
        print(f"Załadowano {count} linków.")

    def load_ratings_from_csv(self, csv_path: str = os.path.join(_csv_dir, "ratings.csv")):
        """Ładuje dane z pliku ratings.csv do bazy danych"""
        cursor = self.conn.cursor()

        # Czyścimy tabelę przed załadowaniem
        cursor.execute("DELETE FROM ratings")

        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                cursor.execute(
                    "INSERT INTO ratings (userId, movieId, rating, timestamp) VALUES (?, ?, ?, ?)",
                    (int(row['userId']), int(row['movieId']), float(row['rating']), int(row['timestamp']))
                )

        self.conn.commit()
        count = cursor.execute("SELECT COUNT(*) FROM ratings").fetchone()[0]
        print(f"Załadowano {count} ocen.")

    def load_tags_from_csv(self, csv_path: str = os.path.join(_csv_dir, "tags.csv")):
        """Ładuje dane z pliku tags.csv do bazy danych"""
        cursor = self.conn.cursor()

        # Czyścimy tabelę przed załadowaniem
        cursor.execute("DELETE FROM tags")

        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                cursor.execute(
                    "INSERT INTO tags (userId, movieId, tag, timestamp) VALUES (?, ?, ?, ?)",
                    (int(row['userId']), int(row['movieId']), row['tag'], int(row['timestamp']))
                )

        self.conn.commit()
        count = cursor.execute("SELECT COUNT(*) FROM tags").fetchone()[0]
        print(f"Załadowano {count} tagów.")

    def load_all_data(self):
        """Ładuje wszystkie dane z plików CSV do bazy danych"""
        print("Rozpoczynam ładowanie danych...")
        self.load_movies_from_csv()
        self.load_links_from_csv()
        self.load_ratings_from_csv()
        self.load_tags_from_csv()
        print("Wszystkie dane zostały załadowane.")

    def get_movies(self):
        """Pobiera wszystkie filmy z bazy danych"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT movieId, title, genres FROM movies")
        return cursor.fetchall()

    def get_links(self):
        """Pobiera wszystkie linki z bazy danych"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT movieId, imdbId, tmdbId FROM links")
        return cursor.fetchall()

    def get_ratings(self):
        """Pobiera wszystkie oceny z bazy danych"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT userId, movieId, rating, timestamp FROM ratings")
        return cursor.fetchall()

    def get_tags(self):
        """Pobiera wszystkie tagi z bazy danych"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT userId, movieId, tag, timestamp FROM tags")
        return cursor.fetchall()


def init_database():
    """Inicjalizuje bazę danych i ładuje dane z plików CSV"""
    db = Database()
    db.connect()
    db.create_schema()
    db.load_all_data()
    db.close()
    print("Baza danych została zainicjalizowana.")


if __name__ == "__main__":
    init_database()
