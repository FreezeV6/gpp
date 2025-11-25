from pydantic import BaseModel


class Movie:
    
    def __init__(self, movie_id: int, title: str, genres: str):
        self.movieId = movie_id
        self.title = title
        self.genres = genres


class MovieCreate(BaseModel):
    movieId: int
    title: str
    genres: str


class MovieUpdate(BaseModel):
    title: str
    genres: str


class Link:
    
    def __init__(self, movie_id: int, imdb_id: str, tmdb_id: str):
        self.movieId = movie_id
        self.imdbId = imdb_id
        self.tmdbId = tmdb_id


class LinkCreate(BaseModel):
    movieId: int
    imdbId: str
    tmdbId: str


class LinkUpdate(BaseModel):
    imdbId: str
    tmdbId: str


class Rating:
    
    def __init__(self, user_id: int, movie_id: int, rating: float, timestamp: int, rating_id: int = None):
        self.id = rating_id
        self.userId = user_id
        self.movieId = movie_id
        self.rating = rating
        self.timestamp = timestamp


class RatingCreate(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: int


class RatingUpdate(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: int


class Tag:
    
    def __init__(self, user_id: int, movie_id: int, tag: str, timestamp: int, tag_id: int = None):
        self.id = tag_id
        self.userId = user_id
        self.movieId = movie_id
        self.tag = tag
        self.timestamp = timestamp


class TagCreate(BaseModel):
    userId: int
    movieId: int
    tag: str
    timestamp: int


class TagUpdate(BaseModel):
    userId: int
    movieId: int
    tag: str
    timestamp: int


