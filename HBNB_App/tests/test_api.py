"""
Tests d'intégration — tous les endpoints API HBnB Part 3.

Utilise le client de test Flask (pas de serveur réel nécessaire).
Chaque test est indépendant grâce à une base SQLite en mémoire réinitialisée.

Lancement :
    cd HBNB_App
    python -m pytest tests/test_api.py -v
"""

import pytest
from app import create_app
from app.extensions import db as _db
from config import Config


# ── Config de test ─────────────────────────────────────────────────────────────

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-secret"


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_token(client):
    """Crée un admin et retourne son JWT."""
    client.post("/api/v1/users/", json={
        "first_name": "Admin",
        "last_name": "HBnB",
        "email": "admin@hbnb.io",
        "password": "Admin1234!",
        "is_admin": True,
    })
    # Force is_admin via DB directement (POST public force is_admin=False)
    from app.extensions import db
    from app.models.user import User
    user = db.session.execute(
        db.select(User).where(User.email == "admin@hbnb.io")
    ).scalars().first()
    user.is_admin = True
    db.session.commit()

    res = client.post("/api/v1/auth/login", json={
        "email": "admin@hbnb.io",
        "password": "Admin1234!",
    })
    return res.json["access_token"]


@pytest.fixture
def user_token(client):
    """Crée un utilisateur standard et retourne son JWT."""
    client.post("/api/v1/users/", json={
        "first_name": "Alice",
        "last_name": "Dupont",
        "email": "alice@example.com",
        "password": "Alice1234!",
    })
    res = client.post("/api/v1/auth/login", json={
        "email": "alice@example.com",
        "password": "Alice1234!",
    })
    return res.json["access_token"]


@pytest.fixture
def user_id(client):
    """Crée un utilisateur et retourne son UUID."""
    res = client.post("/api/v1/users/", json={
        "first_name": "Alice",
        "last_name": "Dupont",
        "email": "alice@example.com",
        "password": "Alice1234!",
    })
    return res.json["id"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════════════════════

class TestAuth:

    def test_login_success(self, client, user_id):
        res = client.post("/api/v1/auth/login", json={
            "email": "alice@example.com",
            "password": "Alice1234!",
        })
        assert res.status_code == 200
        assert "access_token" in res.json

    def test_login_wrong_password(self, client, user_id):
        res = client.post("/api/v1/auth/login", json={
            "email": "alice@example.com",
            "password": "mauvais",
        })
        assert res.status_code == 401

    def test_login_unknown_email(self, client):
        res = client.post("/api/v1/auth/login", json={
            "email": "inconnu@example.com",
            "password": "test",
        })
        assert res.status_code == 401

    def test_login_missing_fields(self, client):
        res = client.post("/api/v1/auth/login", json={"email": "x@x.com"})
        assert res.status_code == 400


# ══════════════════════════════════════════════════════════════════════════════
#  USERS
# ══════════════════════════════════════════════════════════════════════════════

class TestUsers:

    def test_create_user(self, client):
        res = client.post("/api/v1/users/", json={
            "first_name": "Bob",
            "last_name": "Martin",
            "email": "bob@example.com",
            "password": "Bob1234!",
        })
        assert res.status_code == 201
        assert res.json["email"] == "bob@example.com"
        assert "password" not in res.json

    def test_create_user_duplicate_email(self, client, user_id):
        res = client.post("/api/v1/users/", json={
            "first_name": "Alice2",
            "last_name": "Dupont",
            "email": "alice@example.com",
            "password": "Alice1234!",
        })
        assert res.status_code == 400

    def test_create_user_invalid_email(self, client):
        res = client.post("/api/v1/users/", json={
            "first_name": "X",
            "last_name": "Y",
            "email": "pasunemail",
            "password": "test",
        })
        assert res.status_code == 400

    def test_create_user_is_admin_ignored_without_token(self, client):
        res = client.post("/api/v1/users/", json={
            "first_name": "Hacker",
            "last_name": "X",
            "email": "hacker@x.com",
            "password": "test1234",
            "is_admin": True,
        })
        assert res.status_code == 201
        assert res.json["is_admin"] is False

    def test_get_all_users(self, client, user_id):
        res = client.get("/api/v1/users/")
        assert res.status_code == 200
        assert isinstance(res.json, list)
        assert len(res.json) >= 1

    def test_get_user_by_id(self, client, user_id):
        res = client.get(f"/api/v1/users/{user_id}")
        assert res.status_code == 200
        assert res.json["id"] == user_id

    def test_get_user_not_found(self, client):
        res = client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")
        assert res.status_code == 404

    def test_update_user_own_profile(self, client, user_id, user_token):
        res = client.put(f"/api/v1/users/{user_id}",
                         json={"first_name": "Alicia"},
                         headers=auth(user_token))
        assert res.status_code == 200
        assert res.json["first_name"] == "Alicia"

    def test_update_user_cannot_change_email(self, client, user_id, user_token):
        res = client.put(f"/api/v1/users/{user_id}",
                         json={"email": "new@example.com"},
                         headers=auth(user_token))
        assert res.status_code == 400

    def test_update_user_other_profile_forbidden(self, client, user_token):
        other = client.post("/api/v1/users/", json={
            "first_name": "Bob",
            "last_name": "Martin",
            "email": "bob@example.com",
            "password": "Bob1234!",
        })
        other_id = other.json["id"]
        res = client.put(f"/api/v1/users/{other_id}",
                         json={"first_name": "Hacked"},
                         headers=auth(user_token))
        assert res.status_code == 403

    def test_update_user_no_token(self, client, user_id):
        res = client.put(f"/api/v1/users/{user_id}",
                         json={"first_name": "X"})
        assert res.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
#  AMENITIES
# ══════════════════════════════════════════════════════════════════════════════

class TestAmenities:

    def test_get_all_amenities_public(self, client):
        res = client.get("/api/v1/amenities/")
        assert res.status_code == 200
        assert isinstance(res.json, list)

    def test_create_amenity_as_admin(self, client, admin_token):
        res = client.post("/api/v1/amenities/",
                          json={"name": "Jacuzzi"},
                          headers=auth(admin_token))
        assert res.status_code == 201
        assert res.json["name"] == "Jacuzzi"

    def test_create_amenity_as_user_forbidden(self, client, user_token):
        res = client.post("/api/v1/amenities/",
                          json={"name": "Jacuzzi"},
                          headers=auth(user_token))
        assert res.status_code == 403

    def test_create_amenity_no_token(self, client):
        res = client.post("/api/v1/amenities/", json={"name": "Jacuzzi"})
        assert res.status_code == 401

    def test_get_amenity_by_id(self, client, admin_token):
        created = client.post("/api/v1/amenities/",
                              json={"name": "Piscine"},
                              headers=auth(admin_token))
        amenity_id = created.json["id"]
        res = client.get(f"/api/v1/amenities/{amenity_id}")
        assert res.status_code == 200
        assert res.json["name"] == "Piscine"

    def test_get_amenity_not_found(self, client):
        res = client.get("/api/v1/amenities/00000000-0000-0000-0000-000000000000")
        assert res.status_code == 404

    def test_update_amenity_as_admin(self, client, admin_token):
        created = client.post("/api/v1/amenities/",
                              json={"name": "WiFi"},
                              headers=auth(admin_token))
        amenity_id = created.json["id"]
        res = client.put(f"/api/v1/amenities/{amenity_id}",
                         json={"name": "Wi-Fi 6"},
                         headers=auth(admin_token))
        assert res.status_code == 200
        assert res.json["name"] == "Wi-Fi 6"

    def test_update_amenity_as_user_forbidden(self, client, admin_token, user_token):
        created = client.post("/api/v1/amenities/",
                              json={"name": "Parking"},
                              headers=auth(admin_token))
        amenity_id = created.json["id"]
        res = client.put(f"/api/v1/amenities/{amenity_id}",
                         json={"name": "Parking gratuit"},
                         headers=auth(user_token))
        assert res.status_code == 403


# ══════════════════════════════════════════════════════════════════════════════
#  PLACES
# ══════════════════════════════════════════════════════════════════════════════

class TestPlaces:

    @pytest.fixture
    def place_id(self, client, user_id, user_token):
        res = client.post("/api/v1/places/", json={
            "title": "Studio Paris",
            "description": "Sympa",
            "price": 80.0,
            "latitude": 48.85,
            "longitude": 2.35,
            "owner_id": user_id,
            "amenities": [],
        }, headers=auth(user_token))
        return res.json["id"]

    def test_create_place(self, client, user_id, user_token):
        res = client.post("/api/v1/places/", json={
            "title": "Maison Lyon",
            "price": 120.0,
            "latitude": 45.75,
            "longitude": 4.83,
            "owner_id": user_id,
            "amenities": [],
        }, headers=auth(user_token))
        assert res.status_code == 201
        assert res.json["title"] == "Maison Lyon"
        assert res.json["owner"]["email"] == "alice@example.com"

    def test_create_place_wrong_owner(self, client, user_token):
        res = client.post("/api/v1/places/", json={
            "title": "Fraude",
            "price": 50.0,
            "latitude": 10.0,
            "longitude": 10.0,
            "owner_id": "00000000-0000-0000-0000-000000000000",
            "amenities": [],
        }, headers=auth(user_token))
        assert res.status_code == 403

    def test_create_place_no_token(self, client, user_id):
        res = client.post("/api/v1/places/", json={
            "title": "Test",
            "price": 50.0,
            "latitude": 10.0,
            "longitude": 10.0,
            "owner_id": user_id,
            "amenities": [],
        })
        assert res.status_code == 401

    def test_create_place_invalid_price(self, client, user_id, user_token):
        res = client.post("/api/v1/places/", json={
            "title": "Test",
            "price": -10.0,
            "latitude": 10.0,
            "longitude": 10.0,
            "owner_id": user_id,
            "amenities": [],
        }, headers=auth(user_token))
        assert res.status_code == 400

    def test_create_place_invalid_latitude(self, client, user_id, user_token):
        res = client.post("/api/v1/places/", json={
            "title": "Test",
            "price": 50.0,
            "latitude": 200.0,
            "longitude": 10.0,
            "owner_id": user_id,
            "amenities": [],
        }, headers=auth(user_token))
        assert res.status_code == 400

    def test_get_all_places(self, client, place_id):
        res = client.get("/api/v1/places/")
        assert res.status_code == 200
        assert isinstance(res.json, list)
        assert len(res.json) >= 1

    def test_get_place_by_id(self, client, place_id):
        res = client.get(f"/api/v1/places/{place_id}")
        assert res.status_code == 200
        assert res.json["id"] == place_id
        assert "owner" in res.json

    def test_get_place_not_found(self, client):
        res = client.get("/api/v1/places/00000000-0000-0000-0000-000000000000")
        assert res.status_code == 404

    def test_update_place_as_owner(self, client, user_id, user_token, place_id):
        res = client.put(f"/api/v1/places/{place_id}", json={
            "title": "Studio Paris MAJ",
            "price": 90.0,
            "latitude": 48.85,
            "longitude": 2.35,
            "owner_id": user_id,
            "amenities": [],
        }, headers=auth(user_token))
        assert res.status_code == 200
        assert res.json["title"] == "Studio Paris MAJ"

    def test_update_place_as_other_user_forbidden(self, client, place_id):
        other = client.post("/api/v1/users/", json={
            "first_name": "Bob",
            "last_name": "Martin",
            "email": "bob@example.com",
            "password": "Bob1234!",
        })
        other_id = other.json["id"]
        login = client.post("/api/v1/auth/login", json={
            "email": "bob@example.com",
            "password": "Bob1234!",
        })
        bob_token = login.json["access_token"]
        res = client.put(f"/api/v1/places/{place_id}", json={
            "title": "Hacked",
            "price": 1.0,
            "latitude": 0.0,
            "longitude": 0.0,
            "owner_id": other_id,
            "amenities": [],
        }, headers=auth(bob_token))
        assert res.status_code == 403


# ══════════════════════════════════════════════════════════════════════════════
#  REVIEWS
# ══════════════════════════════════════════════════════════════════════════════

class TestReviews:

    @pytest.fixture
    def setup(self, client):
        """Crée Alice (owner), Bob (reviewer), un lieu, et retourne les IDs/tokens."""
        # Alice
        alice = client.post("/api/v1/users/", json={
            "first_name": "Alice", "last_name": "D",
            "email": "alice@example.com", "password": "Alice1234!",
        })
        alice_id = alice.json["id"]
        alice_tok = client.post("/api/v1/auth/login", json={
            "email": "alice@example.com", "password": "Alice1234!",
        }).json["access_token"]

        # Bob
        bob = client.post("/api/v1/users/", json={
            "first_name": "Bob", "last_name": "M",
            "email": "bob@example.com", "password": "Bob1234!",
        })
        bob_tok = client.post("/api/v1/auth/login", json={
            "email": "bob@example.com", "password": "Bob1234!",
        }).json["access_token"]

        # Lieu d'Alice
        place = client.post("/api/v1/places/", json={
            "title": "Studio", "price": 80.0,
            "latitude": 48.85, "longitude": 2.35,
            "owner_id": alice_id, "amenities": [],
        }, headers=auth(alice_tok))
        place_id = place.json["id"]

        return {
            "alice_id": alice_id, "alice_tok": alice_tok,
            "bob_tok": bob_tok, "place_id": place_id,
        }

    def test_create_review(self, client, setup):
        res = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"],
            "text": "Super endroit !",
            "rating": 5,
        }, headers=auth(setup["bob_tok"]))
        assert res.status_code == 201
        assert res.json["rating"] == 5
        assert res.json["user_id"] is not None

    def test_create_review_own_place_forbidden(self, client, setup):
        res = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"],
            "text": "Mon propre lieu",
            "rating": 5,
        }, headers=auth(setup["alice_tok"]))
        assert res.status_code == 403

    def test_create_review_duplicate_forbidden(self, client, setup):
        client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"],
            "text": "Premier avis",
            "rating": 4,
        }, headers=auth(setup["bob_tok"]))
        res = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"],
            "text": "Deuxième avis",
            "rating": 3,
        }, headers=auth(setup["bob_tok"]))
        assert res.status_code == 400

    def test_create_review_invalid_rating(self, client, setup):
        res = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"],
            "text": "Test",
            "rating": 6,
        }, headers=auth(setup["bob_tok"]))
        assert res.status_code == 400

    def test_create_review_no_token(self, client, setup):
        res = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"],
            "text": "Test",
            "rating": 3,
        })
        assert res.status_code == 401

    def test_get_all_reviews(self, client, setup):
        client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"],
            "text": "Bien", "rating": 4,
        }, headers=auth(setup["bob_tok"]))
        res = client.get("/api/v1/reviews/")
        assert res.status_code == 200
        assert len(res.json) >= 1

    def test_get_review_by_id(self, client, setup):
        created = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"],
            "text": "Bien", "rating": 4,
        }, headers=auth(setup["bob_tok"]))
        review_id = created.json["id"]
        res = client.get(f"/api/v1/reviews/{review_id}")
        assert res.status_code == 200
        assert res.json["id"] == review_id

    def test_get_reviews_by_place(self, client, setup):
        client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"],
            "text": "Bien", "rating": 4,
        }, headers=auth(setup["bob_tok"]))
        res = client.get(f"/api/v1/places/{setup['place_id']}/reviews")
        assert res.status_code == 200
        assert len(res.json) >= 1

    def test_update_review_as_author(self, client, setup):
        created = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"],
            "text": "Bien", "rating": 4,
        }, headers=auth(setup["bob_tok"]))
        review_id = created.json["id"]
        res = client.put(f"/api/v1/reviews/{review_id}",
                         json={"text": "Très bien", "rating": 5},
                         headers=auth(setup["bob_tok"]))
        assert res.status_code == 200
        assert res.json["rating"] == 5

    def test_update_review_as_other_forbidden(self, client, setup):
        created = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"],
            "text": "Bien", "rating": 4,
        }, headers=auth(setup["bob_tok"]))
        review_id = created.json["id"]
        res = client.put(f"/api/v1/reviews/{review_id}",
                         json={"text": "Modifié", "rating": 1},
                         headers=auth(setup["alice_tok"]))
        assert res.status_code == 403

    def test_delete_review_as_author(self, client, setup):
        created = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"],
            "text": "Bien", "rating": 4,
        }, headers=auth(setup["bob_tok"]))
        review_id = created.json["id"]
        res = client.delete(f"/api/v1/reviews/{review_id}",
                            headers=auth(setup["bob_tok"]))
        assert res.status_code == 200
        assert client.get(f"/api/v1/reviews/{review_id}").status_code == 404

    def test_delete_review_as_other_forbidden(self, client, setup):
        created = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"],
            "text": "Bien", "rating": 4,
        }, headers=auth(setup["bob_tok"]))
        review_id = created.json["id"]
        res = client.delete(f"/api/v1/reviews/{review_id}",
                            headers=auth(setup["alice_tok"]))
        assert res.status_code == 403
