import sqlite3
import csv
import os

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_default_db_path = os.path.join(_project_root, "database", "movies.db")
_csv_dir = os.path.join(_project_root, "database")


class Database:

    def __init__(self, db_path: str = _default_db_path):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        if self.conn:
            self.conn.close()

    def create_schema(self):
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                movieId INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                genres TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS links (
                movieId INTEGER PRIMARY KEY,
                imdbId TEXT,
                tmdbId TEXT,
                FOREIGN KEY (movieId) REFERENCES movies(movieId)
            )
        ''')

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

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_ratings_movie 
            ON ratings(movieId)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_ratings_user 
            ON ratings(userId)
        ''')

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
        cursor = self.conn.cursor()

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
        cursor = self.conn.cursor()

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
        cursor = self.conn.cursor()

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
        cursor = self.conn.cursor()

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
        print("Rozpoczynam ładowanie danych...")
        self.load_movies_from_csv()
        self.load_links_from_csv()
        self.load_ratings_from_csv()
        self.load_tags_from_csv()
        print("Wszystkie dane zostały załadowane.")

    def get_movies(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT movieId, title, genres FROM movies")
        return cursor.fetchall()

    def get_movie_by_id(self, movie_id: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT movieId, title, genres FROM movies WHERE movieId = ?", (movie_id,))
        return cursor.fetchone()

    def create_movie(self, movie_id: int, title: str, genres: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO movies (movieId, title, genres) VALUES (?, ?, ?)",
            (movie_id, title, genres)
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_movie(self, movie_id: int, title: str, genres: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE movies SET title = ?, genres = ? WHERE movieId = ?",
            (title, genres, movie_id)
        )
        self.conn.commit()
        return cursor.rowcount

    def delete_movie(self, movie_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM movies WHERE movieId = ?", (movie_id,))
        self.conn.commit()
        return cursor.rowcount

    def get_links(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT movieId, imdbId, tmdbId FROM links")
        return cursor.fetchall()

    def get_link_by_id(self, movie_id: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT movieId, imdbId, tmdbId FROM links WHERE movieId = ?", (movie_id,))
        return cursor.fetchone()

    def create_link(self, movie_id: int, imdb_id: str, tmdb_id: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO links (movieId, imdbId, tmdbId) VALUES (?, ?, ?)",
            (movie_id, imdb_id, tmdb_id)
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_link(self, movie_id: int, imdb_id: str, tmdb_id: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE links SET imdbId = ?, tmdbId = ? WHERE movieId = ?",
            (imdb_id, tmdb_id, movie_id)
        )
        self.conn.commit()
        return cursor.rowcount

    def delete_link(self, movie_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM links WHERE movieId = ?", (movie_id,))
        self.conn.commit()
        return cursor.rowcount

    def get_ratings(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, userId, movieId, rating, timestamp FROM ratings")
        return cursor.fetchall()

    def get_rating_by_id(self, rating_id: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, userId, movieId, rating, timestamp FROM ratings WHERE id = ?", (rating_id,))
        return cursor.fetchone()

    def create_rating(self, user_id: int, movie_id: int, rating: float, timestamp: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO ratings (userId, movieId, rating, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, movie_id, rating, timestamp)
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_rating(self, rating_id: int, user_id: int, movie_id: int, rating: float, timestamp: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE ratings SET userId = ?, movieId = ?, rating = ?, timestamp = ? WHERE id = ?",
            (user_id, movie_id, rating, timestamp, rating_id)
        )
        self.conn.commit()
        return cursor.rowcount

    def delete_rating(self, rating_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM ratings WHERE id = ?", (rating_id,))
        self.conn.commit()
        return cursor.rowcount

    def get_tags(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, userId, movieId, tag, timestamp FROM tags")
        return cursor.fetchall()

    def get_tag_by_id(self, tag_id: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, userId, movieId, tag, timestamp FROM tags WHERE id = ?", (tag_id,))
        return cursor.fetchone()

    def create_tag(self, user_id: int, movie_id: int, tag: str, timestamp: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO tags (userId, movieId, tag, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, movie_id, tag, timestamp)
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_tag(self, tag_id: int, user_id: int, movie_id: int, tag: str, timestamp: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE tags SET userId = ?, movieId = ?, tag = ?, timestamp = ? WHERE id = ?",
            (user_id, movie_id, tag, timestamp, tag_id)
        )
        self.conn.commit()
        return cursor.rowcount

    def delete_tag(self, tag_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        self.conn.commit()
        return cursor.rowcount


def init_database():
    db = Database()
    db.connect()
    db.create_schema()
    db.load_all_data()
    db.close()
    print("Baza danych została zainicjalizowana.")


if __name__ == "__main__":
    init_database()
