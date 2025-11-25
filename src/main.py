"""
FastAPI - API dla bazy danych filmów
"""
from fastapi import FastAPI
from src.models import Movie, Link, Rating, Tag
from src.database import Database

app = FastAPI(title="Movies API", version="1.0.0")

# Inicjalizacja połączenia z bazą danych
db = Database()
db.connect()


@app.get("/")
def hello_world():
    return {"hello": "world"}


@app.get("/movies")
def get_movies():
    """Pobiera wszystkie filmy z bazy danych"""
    movies = []
    
    rows = db.get_movies()

    for row in rows:
        movie = Movie(row['movieId'], row['title'], row['genres'])
        movies.append(movie.__dict__)

    return movies


@app.get("/links")
def get_links():
    """Pobiera wszystkie linki z bazy danych"""
    links = []
    
    rows = db.get_links()

    for row in rows:
        link = Link(row['movieId'], row['imdbId'], row['tmdbId'])
        links.append(link.__dict__)

    return links


@app.get("/ratings")
def get_ratings():
    """Pobiera wszystkie oceny z bazy danych"""
    ratings = []
    
    rows = db.get_ratings()

    for row in rows:
        rating_obj = Rating(row['userId'], row['movieId'], row['rating'], row['timestamp'])
        ratings.append(rating_obj.__dict__)

    return ratings


@app.get("/tags")
def get_tags():
    """Pobiera wszystkie tagi z bazy danych"""
    tags = []
    
    rows = db.get_tags()

    for row in rows:
        tag = Tag(row['userId'], row['movieId'], row['tag'], row['timestamp'])
        tags.append(tag.__dict__)

    return tags


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

