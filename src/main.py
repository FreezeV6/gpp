"""
FastAPI - API dla bazy danych filmów
"""
import csv
from fastapi import FastAPI
from models import Movie, Link, Rating, Tag

app = FastAPI(title="Movies API", version="1.0.0")


@app.get("/")
def hello_world():
    return {"hello": "world"}


@app.get("/movies")
def get_movies():
    movies = []
    
    with open("database/movies.csv", "r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        
        for row in csv_reader:
            if len(row) >= 3:
                movie_id = int(row[0])
                title = row[1]
                genres = row[2]
                
                movie = Movie(movie_id, title, genres)
                
                movies.append(movie.__dict__)
    
    return movies


@app.get("/links")
def get_links():
    links = []
    
    with open("database/links.csv", "r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        
        for row in csv_reader:
            if len(row) >= 3:
                movie_id = int(row[0])
                imdb_id = row[1]
                tmdb_id = row[2]
                
                link = Link(movie_id, imdb_id, tmdb_id)
                
                links.append(link.__dict__)
    
    return links


@app.get("/ratings")
def get_ratings():
    ratings = []
    
    with open("database/ratings.csv", "r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        
        for row in csv_reader:
            if len(row) >= 4:
                user_id = int(row[0])
                movie_id = int(row[1])
                rating = float(row[2])
                timestamp = int(row[3])
                
                # Tworzenie obiektu Rating
                rating_obj = Rating(user_id, movie_id, rating, timestamp)
                
                ratings.append(rating_obj.__dict__)
    
    return ratings


@app.get("/tags")
def get_tags():

    tags = []
    
    with open("database/tags.csv", "r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        
        for row in csv_reader:
            if len(row) >= 4:
                user_id = int(row[0])
                movie_id = int(row[1])
                tag_text = row[2]
                timestamp = int(row[3])
                
                tag = Tag(user_id, movie_id, tag_text, timestamp)
                
                tags.append(tag.__dict__)
    
    return tags


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

