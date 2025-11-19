"""
Modele danych dla API filmów
"""


class Movie:
    """Model dla filmu"""
    
    def __init__(self, movie_id: int, title: str, genres: str):
        self.movieId = movie_id
        self.title = title
        self.genres = genres


class Link:
    """Model dla linków do zewnętrznych baz danych"""
    
    def __init__(self, movie_id: int, imdb_id: str, tmdb_id: str):
        self.movieId = movie_id
        self.imdbId = imdb_id
        self.tmdbId = tmdb_id


class Rating:
    """Model dla ocen filmów"""
    
    def __init__(self, user_id: int, movie_id: int, rating: float, timestamp: int):
        self.userId = user_id
        self.movieId = movie_id
        self.rating = rating
        self.timestamp = timestamp


class Tag:
    """Model dla tagów filmów"""
    
    def __init__(self, user_id: int, movie_id: int, tag: str, timestamp: int):
        self.userId = user_id
        self.movieId = movie_id
        self.tag = tag
        self.timestamp = timestamp

