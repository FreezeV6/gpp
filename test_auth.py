import pytest
from fastapi.testclient import TestClient
import json
import os
import tempfile
from src.main import app
from src.database import Database
from src.security import hash_password

@pytest.fixture
def test_db():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = Database(db_path)
        db.connect()
        db.create_schema()

        admin_hashed = hash_password("admin123")
        db.create_user("admin", "admin@test.com", admin_hashed, json.dumps(["ROLE_ADMIN"]))
        
        user_hashed = hash_password("user123")
        db.create_user("user", "user@test.com", user_hashed, json.dumps(["ROLE_USER"]))
        
        yield db
        db.close()


@pytest.fixture
def client(test_db):
    from src import main
    main.db = test_db
    return TestClient(app)


class TestLogin:
    
    def test_login_successful(self, client):
        response = client.post(
            "/login",
            json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "admin"
        assert "ROLE_ADMIN" in data["user"]["roles"]
    
    def test_login_invalid_username(self, client):
        response = client.post(
            "/login",
            json={"username": "nonexistent", "password": "password123"}
        )
        assert response.status_code == 401
        assert "Incorrect username or password!" in response.json()["detail"]
    
    def test_login_invalid_password(self, client):
        response = client.post(
            "/login",
            json={"username": "admin", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "Incorrect username or password!" in response.json()["detail"]
    
    def test_login_user_role(self, client):
        response = client.post(
            "/login",
            json={"username": "user", "password": "user123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["username"] == "user"
        assert "ROLE_USER" in data["user"]["roles"]


class TestCreateUser:
    
    def test_create_user_as_admin(self, client):
        login_response = client.post(
            "/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]

        response = client.post(
            "/users",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "newuser",
                "email": "newuser@test.com",
                "password": "newpass123",
                "roles": ["ROLE_USER"]
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@test.com"
        assert "ROLE_USER" in data["roles"]
    
    def test_create_user_without_token(self, client):
        response = client.post(
            "/users",
            json={
                "username": "newuser",
                "email": "newuser@test.com",
                "password": "newpass123",
                "roles": ["ROLE_USER"]
            }
        )
        assert response.status_code == 403
        assert "Authorization" in response.json()["detail"]
    
    def test_create_user_as_non_admin(self, client):
        login_response = client.post(
            "/login",
            json={"username": "user", "password": "user123"}
        )
        token = login_response.json()["access_token"]

        response = client.post(
            "/users",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "newuser",
                "email": "newuser@test.com",
                "password": "newpass123",
                "roles": ["ROLE_USER"]
            }
        )
        assert response.status_code == 403
        assert "ROLE_ADMIN" in response.json()["detail"]
    
    def test_create_user_duplicate_username(self, client):
        login_response = client.post(
            "/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]

        response = client.post(
            "/users",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "admin",
                "email": "another@test.com",
                "password": "pass123",
                "roles": ["ROLE_USER"]
            }
        )
        assert response.status_code == 400
        assert "już istnieje" in response.json()["detail"]


class TestUserDetails:
    
    def test_get_user_details_with_valid_token(self, client):
        login_response = client.post(
            "/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]

        response = client.get(
            "/user_details",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["email"] == "admin@test.com"
        assert "ROLE_ADMIN" in data["roles"]
    
    def test_get_user_details_without_token(self, client):
        response = client.get("/user_details")
        assert response.status_code == 403
        assert "Authorization" in response.json()["detail"]

    def test_get_user_details_with_invalid_token(self, client):
        response = client.get(
            "/user_details",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 401
        assert "token" in response.json()["detail"].lower()


class TestTokenValidation:
    
    def test_expired_token_handling(self, client, monkeypatch):
        from src import security
        import jwt

        payload = {
            "user_id": 1,
            "username": "admin",
            "email": "admin@test.com",
            "roles": ["ROLE_ADMIN"],
            "exp": 0,
            "iat": 0
        }
        expired_token = jwt.encode(payload, security.SECRET_KEY, algorithm=security.ALGORITHM)
        
        response = client.get(
            "/user_details",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401
        assert "wygasł" in response.json()["detail"].lower()
    
    def test_invalid_token_signature(self, client):
        response = client.get(
            "/user_details",
            headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.invalid"}
        )
        assert response.status_code == 401
        assert "token" in response.json()["detail"].lower()


class TestAuthorizationHeader:
    
    def test_authorization_header_required(self, client):
        response = client.get("/user_details")
        assert response.status_code == 403
    
    def test_bearer_token_format(self, client):
        login_response = client.post(
            "/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]

        response = client.get(
            "/user_details",
            headers={"Authorization": token}
        )
        assert response.status_code == 403


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

