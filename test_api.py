from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"hello": "world"}


def test_get_movies():
    response = client.get("/movies")
    assert response.status_code == 200
    movies = response.json()
    assert len(movies) > 0
    assert "movieId" in movies[0]
    assert "title" in movies[0]
    assert "genres" in movies[0]
    print(f"Pobrano {len(movies)} filmów")


def test_get_links():
    response = client.get("/links")
    assert response.status_code == 200
    links = response.json()
    assert len(links) > 0
    assert "movieId" in links[0]
    assert "imdbId" in links[0]
    assert "tmdbId" in links[0]
    print(f"Pobrano {len(links)} linków")


def test_get_ratings():
    response = client.get("/ratings")
    assert response.status_code == 200
    ratings = response.json()
    assert len(ratings) > 0
    assert "userId" in ratings[0]
    assert "movieId" in ratings[0]
    assert "rating" in ratings[0]
    assert "timestamp" in ratings[0]
    print(f"Pobrano {len(ratings)} ocen")


def test_get_tags():
    response = client.get("/tags")
    assert response.status_code == 200
    tags = response.json()
    assert len(tags) > 0
    assert "userId" in tags[0]
    assert "movieId" in tags[0]
    assert "tag" in tags[0]
    assert "timestamp" in tags[0]
    print(f"Pobrano {len(tags)} tagów")


if __name__ == "__main__":
    print("Rozpoczynam testy API...\n")
    test_root()
    print("Test endpoint główny - OK")
    
    test_get_movies()
    test_get_links()
    test_get_ratings()
    test_get_tags()
    
    print("\nWszystkie testy zakończone sukcesem!")

