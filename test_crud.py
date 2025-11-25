import pytest
from fastapi.testclient import TestClient
from src.main import app, db
import time

client = TestClient(app)

@pytest.fixture(scope="function")
def test_movie():
    movie_data = {
        "movieId": 999999,
        "title": "Test Movie",
        "genres": "Action|Comedy"
    }
    db.delete_movie(movie_data["movieId"])
    yield movie_data
    db.delete_movie(movie_data["movieId"])


@pytest.fixture(scope="function")
def test_link():
    link_data = {
        "movieId": 999998,
        "imdbId": "tt9999999",
        "tmdbId": "999999"
    }
    db.delete_link(link_data["movieId"])
    yield link_data
    db.delete_link(link_data["movieId"])


@pytest.fixture(scope="function")
def test_rating():
    rating_data = {
        "userId": 99999,
        "movieId": 1,
        "rating": 4.5,
        "timestamp": int(time.time())
    }
    yield rating_data


@pytest.fixture(scope="function")
def test_tag():
    tag_data = {
        "userId": 99999,
        "movieId": 1,
        "tag": "test-tag",
        "timestamp": int(time.time())
    }
    yield tag_data


def test_get_movies():
    response = client.get("/movies")
    
    assert response.status_code == 200
    movies = response.json()
    assert len(movies) > 0
    assert "movieId" in movies[0]
    assert "title" in movies[0]
    assert "genres" in movies[0]
    print(f"Pobrano {len(movies)} filmów")


def test_get_movie_by_id():
    all_movies = client.get("/movies").json()
    movie_id = all_movies[0]["movieId"]
    
    response = client.get(f"/movies/{movie_id}")
    
    assert response.status_code == 200
    movie = response.json()
    assert movie["movieId"] == movie_id
    assert "title" in movie
    assert "genres" in movie
    print(f"Pobrano film ID {movie_id}")


def test_get_movie_by_id_not_found():
    response = client.get("/movies/99999999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    print("Poprawnie zwrócono 404 dla nieistniejącego filmu")


def test_create_movie(test_movie):
    response = client.post("/movies", json=test_movie)
    
    assert response.status_code == 201
    created = response.json()
    assert created["movieId"] == test_movie["movieId"]
    assert created["title"] == test_movie["title"]
    assert created["genres"] == test_movie["genres"]

    verify_response = client.get(f"/movies/{test_movie['movieId']}")
    assert verify_response.status_code == 200
    print(f"Utworzono film ID {test_movie['movieId']}")


def test_update_movie(test_movie):
    client.post("/movies", json=test_movie)

    updated_data = {
        "title": "Updated Test Movie",
        "genres": "Drama|Thriller"
    }
    response = client.put(f"/movies/{test_movie['movieId']}", json=updated_data)
    
    assert response.status_code == 200
    updated = response.json()
    assert updated["movieId"] == test_movie["movieId"]
    assert updated["title"] == updated_data["title"]
    assert updated["genres"] == updated_data["genres"]

    verify_response = client.get(f"/movies/{test_movie['movieId']}")
    verified = verify_response.json()
    assert verified["title"] == updated_data["title"]
    print(f"Zaktualizowano film ID {test_movie['movieId']}")


def test_update_movie_not_found():
    updated_data = {
        "title": "Non-existent Movie",
        "genres": "Drama"
    }
    response = client.put("/movies/99999999", json=updated_data)
    
    assert response.status_code == 404
    print("Poprawnie zwrócono 404 przy aktualizacji nieistniejącego filmu")


def test_delete_movie(test_movie):
    client.post("/movies", json=test_movie)

    response = client.delete(f"/movies/{test_movie['movieId']}")
    
    assert response.status_code == 204

    verify_response = client.get(f"/movies/{test_movie['movieId']}")
    assert verify_response.status_code == 404
    print(f"Usunięto film ID {test_movie['movieId']}")


def test_delete_movie_not_found():
    response = client.delete("/movies/99999999")
    
    assert response.status_code == 404
    print("Poprawnie zwrócono 404 przy usuwaniu nieistniejącego filmu")


def test_get_links():
    response = client.get("/links")
    
    assert response.status_code == 200
    links = response.json()
    assert len(links) > 0
    assert "movieId" in links[0]
    assert "imdbId" in links[0]
    assert "tmdbId" in links[0]
    print(f"Pobrano {len(links)} linków")


def test_get_link_by_id():
    all_links = client.get("/links").json()
    movie_id = all_links[0]["movieId"]
    
    response = client.get(f"/links/{movie_id}")
    
    assert response.status_code == 200
    link = response.json()
    assert link["movieId"] == movie_id
    assert "imdbId" in link
    assert "tmdbId" in link
    print(f"Pobrano link dla filmu ID {movie_id}")


def test_get_link_by_id_not_found():
    response = client.get("/links/99999999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    print("Poprawnie zwrócono 404 dla nieistniejącego linku")


def test_create_link(test_link):
    response = client.post("/links", json=test_link)
    
    assert response.status_code == 201
    created = response.json()
    assert created["movieId"] == test_link["movieId"]
    assert created["imdbId"] == test_link["imdbId"]
    assert created["tmdbId"] == test_link["tmdbId"]

    verify_response = client.get(f"/links/{test_link['movieId']}")
    assert verify_response.status_code == 200
    print(f"Utworzono link dla filmu ID {test_link['movieId']}")


def test_update_link(test_link):
    client.post("/links", json=test_link)
    
    updated_data = {
        "imdbId": "tt8888888",
        "tmdbId": "888888"
    }
    response = client.put(f"/links/{test_link['movieId']}", json=updated_data)
    
    assert response.status_code == 200
    updated = response.json()
    assert updated["movieId"] == test_link["movieId"]
    assert updated["imdbId"] == updated_data["imdbId"]
    assert updated["tmdbId"] == updated_data["tmdbId"]

    verify_response = client.get(f"/links/{test_link['movieId']}")
    verified = verify_response.json()
    assert verified["imdbId"] == updated_data["imdbId"]
    print(f"Zaktualizowano link dla filmu ID {test_link['movieId']}")


def test_update_link_not_found():
    updated_data = {
        "imdbId": "tt0000000",
        "tmdbId": "000000"
    }
    response = client.put("/links/99999999", json=updated_data)
    
    assert response.status_code == 404
    print("Poprawnie zwrócono 404 przy aktualizacji nieistniejącego linku")


def test_delete_link(test_link):
    client.post("/links", json=test_link)
    
    response = client.delete(f"/links/{test_link['movieId']}")
    
    assert response.status_code == 204

    verify_response = client.get(f"/links/{test_link['movieId']}")
    assert verify_response.status_code == 404
    print(f"Usunięto link dla filmu ID {test_link['movieId']}")


def test_delete_link_not_found():
    response = client.delete("/links/99999999")
    
    assert response.status_code == 404
    print("Poprawnie zwrócono 404 przy usuwaniu nieistniejącego linku")


def test_get_ratings():
    response = client.get("/ratings")
    
    assert response.status_code == 200
    ratings = response.json()
    assert len(ratings) > 0
    assert "id" in ratings[0]
    assert "userId" in ratings[0]
    assert "movieId" in ratings[0]
    assert "rating" in ratings[0]
    assert "timestamp" in ratings[0]
    print(f"Pobrano {len(ratings)} ocen")


def test_get_rating_by_id():
    all_ratings = client.get("/ratings").json()
    rating_id = all_ratings[0]["id"]
    
    response = client.get(f"/ratings/{rating_id}")
    
    assert response.status_code == 200
    rating = response.json()
    assert rating["id"] == rating_id
    assert "userId" in rating
    assert "movieId" in rating
    assert "rating" in rating
    print(f"Pobrano ocenę ID {rating_id}")


def test_get_rating_by_id_not_found():
    response = client.get("/ratings/99999999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    print("Poprawnie zwrócono 404 dla nieistniejącej oceny")


def test_create_rating(test_rating):
    response = client.post("/ratings", json=test_rating)
    
    assert response.status_code == 201
    created = response.json()
    assert created["userId"] == test_rating["userId"]
    assert created["movieId"] == test_rating["movieId"]
    assert created["rating"] == test_rating["rating"]
    assert created["timestamp"] == test_rating["timestamp"]
    assert "id" in created

    rating_id = created["id"]
    verify_response = client.get(f"/ratings/{rating_id}")
    assert verify_response.status_code == 200

    client.delete(f"/ratings/{rating_id}")
    print(f"Utworzono ocenę ID {rating_id}")


def test_update_rating(test_rating):
    create_response = client.post("/ratings", json=test_rating)
    rating_id = create_response.json()["id"]
    
    updated_data = {
        "userId": test_rating["userId"],
        "movieId": test_rating["movieId"],
        "rating": 5.0,
        "timestamp": test_rating["timestamp"] + 100
    }
    response = client.put(f"/ratings/{rating_id}", json=updated_data)
    
    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] == rating_id
    assert updated["rating"] == updated_data["rating"]
    assert updated["timestamp"] == updated_data["timestamp"]

    verify_response = client.get(f"/ratings/{rating_id}")
    verified = verify_response.json()
    assert verified["rating"] == updated_data["rating"]

    client.delete(f"/ratings/{rating_id}")
    print(f"Zaktualizowano ocenę ID {rating_id}")


def test_update_rating_not_found():
    updated_data = {
        "userId": 1,
        "movieId": 1,
        "rating": 5.0,
        "timestamp": int(time.time())
    }
    response = client.put("/ratings/99999999", json=updated_data)
    
    assert response.status_code == 404
    print("Poprawnie zwrócono 404 przy aktualizacji nieistniejącej oceny")


def test_delete_rating(test_rating):
    create_response = client.post("/ratings", json=test_rating)
    rating_id = create_response.json()["id"]
    
    response = client.delete(f"/ratings/{rating_id}")
    
    assert response.status_code == 204

    verify_response = client.get(f"/ratings/{rating_id}")
    assert verify_response.status_code == 404
    print(f"Usunięto ocenę ID {rating_id}")


def test_delete_rating_not_found():
    response = client.delete("/ratings/99999999")
    
    assert response.status_code == 404
    print("Poprawnie zwrócono 404 przy usuwaniu nieistniejącej oceny")


def test_get_tags():
    response = client.get("/tags")
    
    assert response.status_code == 200
    tags = response.json()
    assert len(tags) > 0
    assert "id" in tags[0]
    assert "userId" in tags[0]
    assert "movieId" in tags[0]
    assert "tag" in tags[0]
    assert "timestamp" in tags[0]
    print(f"Pobrano {len(tags)} tagów")


def test_get_tag_by_id():
    all_tags = client.get("/tags").json()
    tag_id = all_tags[0]["id"]
    
    response = client.get(f"/tags/{tag_id}")
    
    assert response.status_code == 200
    tag = response.json()
    assert tag["id"] == tag_id
    assert "userId" in tag
    assert "movieId" in tag
    assert "tag" in tag
    print(f"Pobrano tag ID {tag_id}")


def test_get_tag_by_id_not_found():
    response = client.get("/tags/99999999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
    print("Poprawnie zwrócono 404 dla nieistniejącego tagu")


def test_create_tag(test_tag):
    response = client.post("/tags", json=test_tag)
    
    assert response.status_code == 201
    created = response.json()
    assert created["userId"] == test_tag["userId"]
    assert created["movieId"] == test_tag["movieId"]
    assert created["tag"] == test_tag["tag"]
    assert created["timestamp"] == test_tag["timestamp"]
    assert "id" in created

    tag_id = created["id"]
    verify_response = client.get(f"/tags/{tag_id}")
    assert verify_response.status_code == 200

    client.delete(f"/tags/{tag_id}")
    print(f"Utworzono tag ID {tag_id}")


def test_update_tag(test_tag):
    create_response = client.post("/tags", json=test_tag)
    tag_id = create_response.json()["id"]
    
    updated_data = {
        "userId": test_tag["userId"],
        "movieId": test_tag["movieId"],
        "tag": "updated-tag",
        "timestamp": test_tag["timestamp"] + 100
    }
    response = client.put(f"/tags/{tag_id}", json=updated_data)
    
    assert response.status_code == 200
    updated = response.json()
    assert updated["id"] == tag_id
    assert updated["tag"] == updated_data["tag"]
    assert updated["timestamp"] == updated_data["timestamp"]

    verify_response = client.get(f"/tags/{tag_id}")
    verified = verify_response.json()
    assert verified["tag"] == updated_data["tag"]

    client.delete(f"/tags/{tag_id}")
    print(f"Zaktualizowano tag ID {tag_id}")


def test_update_tag_not_found():
    updated_data = {
        "userId": 1,
        "movieId": 1,
        "tag": "non-existent",
        "timestamp": int(time.time())
    }
    response = client.put("/tags/99999999", json=updated_data)
    
    assert response.status_code == 404
    print("Poprawnie zwrócono 404 przy aktualizacji nieistniejącego tagu")


def test_delete_tag(test_tag):
    create_response = client.post("/tags", json=test_tag)
    tag_id = create_response.json()["id"]
    
    response = client.delete(f"/tags/{tag_id}")
    
    assert response.status_code == 204

    verify_response = client.get(f"/tags/{tag_id}")
    assert verify_response.status_code == 404
    print(f"Usunięto tag ID {tag_id}")


def test_delete_tag_not_found():
    response = client.delete("/tags/99999999")
    
    assert response.status_code == 404
    print("Poprawnie zwrócono 404 przy usuwaniu nieistniejącego tagu")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

