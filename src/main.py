from fastapi import FastAPI, HTTPException, Depends
import uvicorn
from src.models import (
    Movie, Link, Rating, Tag,
    MovieCreate, MovieUpdate,
    LinkCreate, LinkUpdate,
    RatingCreate, RatingUpdate,
    TagCreate, TagUpdate,
    UserCreate, LoginRequest, TokenResponse, UserResponse
)
from src.database import Database
from src.security import (
    hash_password, verify_password, create_access_token,
    get_current_user, get_current_admin
)

app = FastAPI(title="Movies API", version="1.0.0")

db = Database()
db.connect()

@app.get("/")
def hello_world():
    return {"hello": "world"}


@app.get("/movies")
def get_movies():
    movies = []
    
    rows = db.get_movies()

    for row in rows:
        movie = Movie(row['movieId'], row['title'], row['genres'])
        movies.append(movie.__dict__)

    return movies


@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    row = db.get_movie_by_id(movie_id)

    if row is None:
        raise HTTPException(status_code=404, detail="Movie not found")

    movie = Movie(row['movieId'], row['title'], row['genres'])
    return movie.__dict__


@app.post("/movies", status_code=201)
def create_movie(movie: MovieCreate):
    try:
        db.create_movie(movie.movieId, movie.title, movie.genres)
        created_movie = Movie(movie.movieId, movie.title, movie.genres)
        return created_movie.__dict__
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, movie: MovieUpdate):
    rows_affected = db.update_movie(movie_id, movie.title, movie.genres)

    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Movie not found")

    updated_movie = Movie(movie_id, movie.title, movie.genres)
    return updated_movie.__dict__


@app.delete("/movies/{movie_id}", status_code=204)
def delete_movie(movie_id: int):
    rows_affected = db.delete_movie(movie_id)

    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Movie not found")

    return None


@app.get("/links")
def get_links():
    links = []
    
    rows = db.get_links()

    for row in rows:
        link = Link(row['movieId'], row['imdbId'], row['tmdbId'])
        links.append(link.__dict__)

    return links


@app.get("/links/{movie_id}")
def get_link(movie_id: int):
    row = db.get_link_by_id(movie_id)

    if row is None:
        raise HTTPException(status_code=404, detail="Link not found")

    link = Link(row['movieId'], row['imdbId'], row['tmdbId'])
    return link.__dict__


@app.post("/links", status_code=201)
def create_link(link: LinkCreate):
    try:
        db.create_link(link.movieId, link.imdbId, link.tmdbId)
        created_link = Link(link.movieId, link.imdbId, link.tmdbId)
        return created_link.__dict__
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/links/{movie_id}")
def update_link(movie_id: int, link: LinkUpdate):
    rows_affected = db.update_link(movie_id, link.imdbId, link.tmdbId)

    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Link not found")

    updated_link = Link(movie_id, link.imdbId, link.tmdbId)
    return updated_link.__dict__


@app.delete("/links/{movie_id}", status_code=204)
def delete_link(movie_id: int):
    rows_affected = db.delete_link(movie_id)

    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Link not found")

    return None


@app.get("/ratings")
def get_ratings():
    ratings = []
    
    rows = db.get_ratings()

    for row in rows:
        rating_obj = Rating(row['userId'], row['movieId'], row['rating'], row['timestamp'], row['id'])
        ratings.append(rating_obj.__dict__)

    return ratings


@app.get("/ratings/{rating_id}")
def get_rating(rating_id: int):
    row = db.get_rating_by_id(rating_id)

    if row is None:
        raise HTTPException(status_code=404, detail="Rating not found")

    rating_obj = Rating(row['userId'], row['movieId'], row['rating'], row['timestamp'], row['id'])
    return rating_obj.__dict__


@app.post("/ratings", status_code=201)
def create_rating(rating: RatingCreate):
    try:
        rating_id = db.create_rating(rating.userId, rating.movieId, rating.rating, rating.timestamp)
        created_rating = Rating(rating.userId, rating.movieId, rating.rating, rating.timestamp, rating_id)
        return created_rating.__dict__
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/ratings/{rating_id}")
def update_rating(rating_id: int, rating: RatingUpdate):
    rows_affected = db.update_rating(rating_id, rating.userId, rating.movieId, rating.rating, rating.timestamp)

    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Rating not found")

    updated_rating = Rating(rating.userId, rating.movieId, rating.rating, rating.timestamp, rating_id)
    return updated_rating.__dict__


@app.delete("/ratings/{rating_id}", status_code=204)
def delete_rating(rating_id: int):
    rows_affected = db.delete_rating(rating_id)

    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Rating not found")

    return None


@app.get("/tags")
def get_tags():
    tags = []
    
    rows = db.get_tags()

    for row in rows:
        tag = Tag(row['userId'], row['movieId'], row['tag'], row['timestamp'], row['id'])
        tags.append(tag.__dict__)

    return tags


@app.get("/tags/{tag_id}")
def get_tag(tag_id: int):
    row = db.get_tag_by_id(tag_id)

    if row is None:
        raise HTTPException(status_code=404, detail="Tag not found")

    tag = Tag(row['userId'], row['movieId'], row['tag'], row['timestamp'], row['id'])
    return tag.__dict__


@app.post("/tags", status_code=201)
def create_tag(tag: TagCreate):
    try:
        tag_id = db.create_tag(tag.userId, tag.movieId, tag.tag, tag.timestamp)
        created_tag = Tag(tag.userId, tag.movieId, tag.tag, tag.timestamp, tag_id)
        return created_tag.__dict__
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/tags/{tag_id}")
def update_tag(tag_id: int, tag: TagUpdate):
    rows_affected = db.update_tag(tag_id, tag.userId, tag.movieId, tag.tag, tag.timestamp)

    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Tag not found")

    updated_tag = Tag(tag.userId, tag.movieId, tag.tag, tag.timestamp, tag_id)
    return updated_tag.__dict__


@app.delete("/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: int):
    rows_affected = db.delete_tag(tag_id)

    if rows_affected == 0:
        raise HTTPException(status_code=404, detail="Tag not found")

    return None


@app.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    user_row = db.get_user_by_username(request.username)

    if user_row is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password!")

    if not verify_password(request.password, user_row['hashed_password']):
        raise HTTPException(status_code=401, detail="Incorrect username or password!")

    import json
    roles = json.loads(user_row['roles']) if user_row['roles'] else []

    access_token = create_access_token(
        user_id=user_row['id'],
        username=user_row['username'],
        email=user_row['email'],
        roles=roles
    )

    user_response = UserResponse(
        id=user_row['id'],
        username=user_row['username'],
        email=user_row['email'],
        roles=roles
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )


@app.post("/users", status_code=201, response_model=UserResponse)
def create_user(user: UserCreate, current_admin: dict = Depends(get_current_admin)):
    import json

    existing_user = db.get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Użytkownik już istnieje")

    hashed_password = hash_password(user.password)

    roles_json = json.dumps(user.roles)

    user_id = db.create_user(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        roles=roles_json
    )

    return UserResponse(
        id=user_id,
        username=user.username,
        email=user.email,
        roles=user.roles
    )


@app.get("/user_details", response_model=UserResponse)
def get_user_details(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user['user_id'],
        username=current_user['username'],
        email=current_user['email'],
        roles=current_user['roles']
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

