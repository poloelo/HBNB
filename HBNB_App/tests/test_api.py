"""
Tests d'intégration — tous les endpoints API HBnB Part 3.
Base SQLite en mémoire, réinitialisée à chaque test.

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
    JWT_SECRET_KEY = "test-secret-key-long-enough-32chars!!"


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


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def create_user(client, email="alice@test.com", first="Alice", last="D", password="Pass1234!"):
    res = client.post("/api/v1/users/", json={
        "first_name": first, "last_name": last,
        "email": email, "password": password,
    })
    assert res.status_code == 201
    return res.json


def login(client, email, password="Pass1234!"):
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    return res.json["access_token"]


def make_admin(app, email):
    """Force is_admin=True directement en DB."""
    from app.extensions import db
    from app.models.user import User
    with app.app_context():
        user = db.session.execute(
            db.select(User).where(User.email == email)
        ).scalars().first()
        user.is_admin = True
        db.session.commit()


def create_admin(client, app, email="admin@test.com"):
    u = create_user(client, email=email, first="Admin", last="X")
    make_admin(app, email)
    token = login(client, email)
    return u, token


def create_amenity(client, token, name="Wi-Fi"):
    res = client.post("/api/v1/amenities/", json={"name": name}, headers=auth(token))
    assert res.status_code == 201
    return res.json


def create_place(client, token, owner_id, amenity_ids=None, **kwargs):
    data = {
        "title": kwargs.get("title", "Studio"),
        "description": kwargs.get("description", "Desc"),
        "price": kwargs.get("price", 80.0),
        "latitude": kwargs.get("latitude", 48.85),
        "longitude": kwargs.get("longitude", 2.35),
        "owner_id": owner_id,
        "amenities": amenity_ids or [],
    }
    res = client.post("/api/v1/places/", json=data, headers=auth(token))
    return res


# ══════════════════════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════════════════════

class TestAuth:

    def test_login_success(self, client):
        create_user(client)
        res = client.post("/api/v1/auth/login", json={
            "email": "alice@test.com", "password": "Pass1234!"
        })
        assert res.status_code == 200
        assert "access_token" in res.json

    def test_login_wrong_password(self, client):
        create_user(client)
        res = client.post("/api/v1/auth/login", json={
            "email": "alice@test.com", "password": "wrong"
        })
        assert res.status_code == 401

    def test_login_unknown_email(self, client):
        res = client.post("/api/v1/auth/login", json={
            "email": "nobody@test.com", "password": "test"
        })
        assert res.status_code == 401

    def test_login_missing_password(self, client):
        res = client.post("/api/v1/auth/login", json={"email": "x@x.com"})
        assert res.status_code == 400

    def test_login_missing_email(self, client):
        res = client.post("/api/v1/auth/login", json={"password": "test"})
        assert res.status_code == 400

    def test_token_contains_is_admin_false(self, client):
        create_user(client)
        res = client.post("/api/v1/auth/login", json={
            "email": "alice@test.com", "password": "Pass1234!"
        })
        import base64, json as j
        payload = res.json["access_token"].split(".")[1]
        payload += "=" * (4 - len(payload) % 4)
        claims = j.loads(base64.b64decode(payload))
        assert claims["is_admin"] is False

    def test_token_contains_is_admin_true(self, client, app):
        _, token = create_admin(client, app)
        import base64, json as j
        payload = token.split(".")[1]
        payload += "=" * (4 - len(payload) % 4)
        claims = j.loads(base64.b64decode(payload))
        assert claims["is_admin"] is True


# ══════════════════════════════════════════════════════════════════════════════
#  USERS
# ══════════════════════════════════════════════════════════════════════════════

class TestUsers:

    def test_create_user_basic(self, client):
        res = client.post("/api/v1/users/", json={
            "first_name": "Bob", "last_name": "M",
            "email": "bob@test.com", "password": "Pass1234!",
        })
        assert res.status_code == 201
        assert res.json["email"] == "bob@test.com"
        assert "password" not in res.json
        assert res.json["is_admin"] is False
        assert "id" in res.json
        assert "created_at" in res.json

    def test_create_user_is_admin_ignored_without_token(self, client):
        res = client.post("/api/v1/users/", json={
            "first_name": "H", "last_name": "X",
            "email": "h@test.com", "password": "Pass1234!",
            "is_admin": True,
        })
        assert res.status_code == 201
        assert res.json["is_admin"] is False

    def test_create_user_admin_can_set_is_admin(self, client, app):
        _, admin_token = create_admin(client, app)
        res = client.post("/api/v1/users/",
            json={"first_name": "S", "last_name": "U",
                  "email": "super@test.com", "password": "Pass1234!",
                  "is_admin": True},
            headers=auth(admin_token))
        assert res.status_code == 201
        assert res.json["is_admin"] is True

    def test_create_user_duplicate_email(self, client):
        create_user(client)
        res = client.post("/api/v1/users/", json={
            "first_name": "A2", "last_name": "D",
            "email": "alice@test.com", "password": "Pass1234!",
        })
        assert res.status_code == 400

    def test_create_user_invalid_email(self, client):
        res = client.post("/api/v1/users/", json={
            "first_name": "X", "last_name": "Y",
            "email": "pasunemail", "password": "test",
        })
        assert res.status_code == 400

    def test_create_user_missing_fields(self, client):
        res = client.post("/api/v1/users/", json={"email": "x@x.com"})
        assert res.status_code == 400

    def test_get_all_users_public(self, client):
        create_user(client)
        res = client.get("/api/v1/users/")
        assert res.status_code == 200
        assert isinstance(res.json, list)
        assert len(res.json) == 1

    def test_get_user_by_id(self, client):
        u = create_user(client)
        res = client.get(f"/api/v1/users/{u['id']}")
        assert res.status_code == 200
        assert res.json["id"] == u["id"]
        assert "password" not in res.json

    def test_get_user_not_found(self, client):
        res = client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")
        assert res.status_code == 404

    def test_update_user_own_profile(self, client):
        u = create_user(client)
        token = login(client, "alice@test.com")
        res = client.put(f"/api/v1/users/{u['id']}",
                         json={"first_name": "Alicia", "last_name": "D"},
                         headers=auth(token))
        assert res.status_code == 200
        assert res.json["first_name"] == "Alicia"

    def test_update_user_cannot_change_email_as_user(self, client):
        u = create_user(client)
        token = login(client, "alice@test.com")
        res = client.put(f"/api/v1/users/{u['id']}",
                         json={"email": "new@test.com"},
                         headers=auth(token))
        assert res.status_code == 400

    def test_update_user_cannot_change_password_as_user(self, client):
        u = create_user(client)
        token = login(client, "alice@test.com")
        res = client.put(f"/api/v1/users/{u['id']}",
                         json={"password": "NewPass1234!"},
                         headers=auth(token))
        assert res.status_code == 400

    def test_update_user_other_profile_forbidden(self, client):
        create_user(client, email="alice@test.com")
        token = login(client, "alice@test.com")
        bob = create_user(client, email="bob@test.com", first="Bob", last="M")
        res = client.put(f"/api/v1/users/{bob['id']}",
                         json={"first_name": "Hacked"},
                         headers=auth(token))
        assert res.status_code == 403

    def test_update_user_no_token(self, client):
        u = create_user(client)
        res = client.put(f"/api/v1/users/{u['id']}",
                         json={"first_name": "X"})
        assert res.status_code == 401

    def test_admin_can_update_any_user_email(self, client, app):
        u = create_user(client, email="alice@test.com")
        _, admin_token = create_admin(client, app)
        res = client.put(f"/api/v1/users/{u['id']}",
                         json={"email": "newalice@test.com"},
                         headers=auth(admin_token))
        assert res.status_code == 200
        assert res.json["email"] == "newalice@test.com"

    def test_admin_can_update_any_user_password(self, client, app):
        u = create_user(client, email="alice@test.com")
        _, admin_token = create_admin(client, app)
        res = client.put(f"/api/v1/users/{u['id']}",
                         json={"password": "NewPass999!"},
                         headers=auth(admin_token))
        assert res.status_code == 200
        # Vérifie que le nouveau mot de passe fonctionne
        login_res = client.post("/api/v1/auth/login", json={
            "email": "alice@test.com", "password": "NewPass999!"
        })
        assert login_res.status_code == 200


# ══════════════════════════════════════════════════════════════════════════════
#  AMENITIES
# ══════════════════════════════════════════════════════════════════════════════

class TestAmenities:

    def test_get_all_amenities_public(self, client):
        res = client.get("/api/v1/amenities/")
        assert res.status_code == 200
        assert isinstance(res.json, list)

    def test_create_amenity_as_admin(self, client, app):
        _, admin_token = create_admin(client, app)
        res = client.post("/api/v1/amenities/",
                          json={"name": "Jacuzzi"},
                          headers=auth(admin_token))
        assert res.status_code == 201
        assert res.json["name"] == "Jacuzzi"
        assert "id" in res.json

    def test_create_amenity_as_user_forbidden(self, client):
        create_user(client)
        token = login(client, "alice@test.com")
        res = client.post("/api/v1/amenities/",
                          json={"name": "Piscine"},
                          headers=auth(token))
        assert res.status_code == 403

    def test_create_amenity_no_token(self, client):
        res = client.post("/api/v1/amenities/", json={"name": "Parking"})
        assert res.status_code == 401

    def test_create_amenity_empty_name(self, client, app):
        _, admin_token = create_admin(client, app)
        res = client.post("/api/v1/amenities/",
                          json={"name": ""},
                          headers=auth(admin_token))
        assert res.status_code == 400

    def test_get_amenity_by_id(self, client, app):
        _, admin_token = create_admin(client, app)
        a = create_amenity(client, admin_token, "Piscine")
        res = client.get(f"/api/v1/amenities/{a['id']}")
        assert res.status_code == 200
        assert res.json["name"] == "Piscine"

    def test_get_amenity_not_found(self, client):
        res = client.get("/api/v1/amenities/00000000-0000-0000-0000-000000000000")
        assert res.status_code == 404

    def test_update_amenity_as_admin(self, client, app):
        _, admin_token = create_admin(client, app)
        a = create_amenity(client, admin_token, "WiFi")
        res = client.put(f"/api/v1/amenities/{a['id']}",
                         json={"name": "Wi-Fi 6"},
                         headers=auth(admin_token))
        assert res.status_code == 200
        assert res.json["name"] == "Wi-Fi 6"

    def test_update_amenity_as_user_forbidden(self, client, app):
        _, admin_token = create_admin(client, app)
        a = create_amenity(client, admin_token, "Parking")
        create_user(client)
        user_token = login(client, "alice@test.com")
        res = client.put(f"/api/v1/amenities/{a['id']}",
                         json={"name": "Parking gratuit"},
                         headers=auth(user_token))
        assert res.status_code == 403

    def test_update_amenity_not_found(self, client, app):
        _, admin_token = create_admin(client, app)
        res = client.put("/api/v1/amenities/00000000-0000-0000-0000-000000000000",
                         json={"name": "X"},
                         headers=auth(admin_token))
        assert res.status_code == 404

    def test_update_amenity_no_token(self, client, app):
        _, admin_token = create_admin(client, app)
        a = create_amenity(client, admin_token, "Spa")
        res = client.put(f"/api/v1/amenities/{a['id']}", json={"name": "X"})
        assert res.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
#  PLACES
# ══════════════════════════════════════════════════════════════════════════════

class TestPlaces:

    def test_create_place_basic(self, client):
        u = create_user(client)
        token = login(client, "alice@test.com")
        res = create_place(client, token, u["id"])
        assert res.status_code == 201
        assert res.json["title"] == "Studio"
        assert res.json["owner"]["email"] == "alice@test.com"
        assert res.json["owner"]["id"] == u["id"]
        assert isinstance(res.json["amenities"], list)

    def test_create_place_with_amenities(self, client, app):
        u = create_user(client)
        token = login(client, "alice@test.com")
        _, admin_token = create_admin(client, app)
        a1 = create_amenity(client, admin_token, "Wi-Fi")
        a2 = create_amenity(client, admin_token, "Piscine")
        res = create_place(client, token, u["id"], amenity_ids=[a1["id"], a2["id"]])
        assert res.status_code == 201
        names = [a["name"] for a in res.json["amenities"]]
        assert "Wi-Fi" in names
        assert "Piscine" in names

    def test_create_place_wrong_owner_id(self, client):
        u = create_user(client)
        token = login(client, "alice@test.com")
        res = create_place(client, token, "00000000-0000-0000-0000-000000000000")
        assert res.status_code == 403

    def test_create_place_no_token(self, client):
        u = create_user(client)
        res = client.post("/api/v1/places/", json={
            "title": "Test", "price": 50.0, "latitude": 10.0,
            "longitude": 10.0, "owner_id": u["id"], "amenities": [],
        })
        assert res.status_code == 401

    def test_create_place_price_zero(self, client):
        u = create_user(client)
        token = login(client, "alice@test.com")
        res = create_place(client, token, u["id"], price=0)
        assert res.status_code == 400

    def test_create_place_price_negative(self, client):
        u = create_user(client)
        token = login(client, "alice@test.com")
        res = create_place(client, token, u["id"], price=-10)
        assert res.status_code == 400

    def test_create_place_invalid_latitude(self, client):
        u = create_user(client)
        token = login(client, "alice@test.com")
        res = create_place(client, token, u["id"], latitude=200.0)
        assert res.status_code == 400

    def test_create_place_invalid_longitude(self, client):
        u = create_user(client)
        token = login(client, "alice@test.com")
        res = create_place(client, token, u["id"], longitude=300.0)
        assert res.status_code == 400

    def test_create_place_nonexistent_owner_as_admin(self, client, app):
        _, admin_token = create_admin(client, app)
        res = client.post("/api/v1/places/", json={
            "title": "Test", "price": 50.0, "latitude": 10.0,
            "longitude": 10.0,
            "owner_id": "00000000-0000-0000-0000-000000000000",
            "amenities": [],
        }, headers=auth(admin_token))
        assert res.status_code == 400

    def test_admin_can_create_place_for_other_user(self, client, app):
        u = create_user(client)
        _, admin_token = create_admin(client, app)
        res = client.post("/api/v1/places/", json={
            "title": "Admin place", "price": 50.0, "latitude": 10.0,
            "longitude": 10.0, "owner_id": u["id"], "amenities": [],
        }, headers=auth(admin_token))
        assert res.status_code == 201
        assert res.json["owner"]["id"] == u["id"]

    def test_get_all_places_public(self, client):
        u = create_user(client)
        token = login(client, "alice@test.com")
        create_place(client, token, u["id"])
        res = client.get("/api/v1/places/")
        assert res.status_code == 200
        assert len(res.json) == 1

    def test_get_place_by_id_includes_owner(self, client):
        u = create_user(client)
        token = login(client, "alice@test.com")
        p = create_place(client, token, u["id"]).json
        res = client.get(f"/api/v1/places/{p['id']}")
        assert res.status_code == 200
        assert res.json["owner"]["id"] == u["id"]
        assert res.json["owner"]["email"] == "alice@test.com"

    def test_get_place_by_id_includes_amenities(self, client, app):
        u = create_user(client)
        token = login(client, "alice@test.com")
        _, admin_token = create_admin(client, app)
        a = create_amenity(client, admin_token, "Spa")
        p = create_place(client, token, u["id"], amenity_ids=[a["id"]]).json
        res = client.get(f"/api/v1/places/{p['id']}")
        assert res.status_code == 200
        assert any(am["name"] == "Spa" for am in res.json["amenities"])

    def test_get_place_not_found(self, client):
        res = client.get("/api/v1/places/00000000-0000-0000-0000-000000000000")
        assert res.status_code == 404

    def test_update_place_as_owner(self, client):
        u = create_user(client)
        token = login(client, "alice@test.com")
        p = create_place(client, token, u["id"]).json
        res = client.put(f"/api/v1/places/{p['id']}", json={
            "title": "Studio MAJ", "price": 99.0,
            "latitude": 48.85, "longitude": 2.35,
            "owner_id": u["id"], "amenities": [],
        }, headers=auth(token))
        assert res.status_code == 200
        assert res.json["title"] == "Studio MAJ"
        assert res.json["price"] == 99.0

    def test_update_place_with_amenities(self, client, app):
        """Le vrai bug : PUT /places/ avec une liste d'UUIDs d'amenities."""
        u = create_user(client)
        token = login(client, "alice@test.com")
        _, admin_token = create_admin(client, app)
        a = create_amenity(client, admin_token, "Jacuzzi")
        p = create_place(client, token, u["id"]).json
        res = client.put(f"/api/v1/places/{p['id']}", json={
            "title": "Studio", "price": 80.0,
            "latitude": 48.85, "longitude": 2.35,
            "owner_id": u["id"],
            "amenities": [a["id"]],
        }, headers=auth(token))
        assert res.status_code == 200
        assert any(am["name"] == "Jacuzzi" for am in res.json["amenities"])

    def test_update_place_remove_amenities(self, client, app):
        u = create_user(client)
        token = login(client, "alice@test.com")
        _, admin_token = create_admin(client, app)
        a = create_amenity(client, admin_token, "Wi-Fi")
        p = create_place(client, token, u["id"], amenity_ids=[a["id"]]).json
        res = client.put(f"/api/v1/places/{p['id']}", json={
            "title": "Studio", "price": 80.0,
            "latitude": 48.85, "longitude": 2.35,
            "owner_id": u["id"], "amenities": [],
        }, headers=auth(token))
        assert res.status_code == 200
        assert res.json["amenities"] == []

    def test_update_place_as_other_user_forbidden(self, client):
        alice = create_user(client, email="alice@test.com")
        alice_token = login(client, "alice@test.com")
        p = create_place(client, alice_token, alice["id"]).json
        bob = create_user(client, email="bob@test.com", first="Bob", last="M")
        bob_token = login(client, "bob@test.com")
        res = client.put(f"/api/v1/places/{p['id']}", json={
            "title": "Hacked", "price": 1.0,
            "latitude": 0.0, "longitude": 0.0,
            "owner_id": bob["id"], "amenities": [],
        }, headers=auth(bob_token))
        assert res.status_code == 403

    def test_update_place_as_admin(self, client, app):
        u = create_user(client)
        token = login(client, "alice@test.com")
        p = create_place(client, token, u["id"]).json
        _, admin_token = create_admin(client, app)
        res = client.put(f"/api/v1/places/{p['id']}", json={
            "title": "Admin edit", "price": 50.0,
            "latitude": 48.85, "longitude": 2.35,
            "owner_id": u["id"], "amenities": [],
        }, headers=auth(admin_token))
        assert res.status_code == 200
        assert res.json["title"] == "Admin edit"

    def test_update_place_no_token(self, client):
        u = create_user(client)
        token = login(client, "alice@test.com")
        p = create_place(client, token, u["id"]).json
        res = client.put(f"/api/v1/places/{p['id']}", json={
            "title": "X", "price": 50.0, "latitude": 0.0,
            "longitude": 0.0, "owner_id": u["id"], "amenities": [],
        })
        assert res.status_code == 401

    def test_update_place_not_found(self, client, app):
        _, admin_token = create_admin(client, app)
        u = create_user(client)
        res = client.put("/api/v1/places/00000000-0000-0000-0000-000000000000", json={
            "title": "X", "price": 50.0, "latitude": 0.0,
            "longitude": 0.0, "owner_id": u["id"], "amenities": [],
        }, headers=auth(admin_token))
        assert res.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
#  REVIEWS
# ══════════════════════════════════════════════════════════════════════════════

class TestReviews:

    @pytest.fixture
    def setup(self, client):
        alice = create_user(client, email="alice@test.com")
        alice_token = login(client, "alice@test.com")
        bob = create_user(client, email="bob@test.com", first="Bob", last="M")
        bob_token = login(client, "bob@test.com")
        p = create_place(client, alice_token, alice["id"]).json
        return {
            "alice_id": alice["id"], "alice_token": alice_token,
            "bob_id": bob["id"], "bob_token": bob_token,
            "place_id": p["id"],
        }

    def test_create_review(self, client, setup):
        res = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "Super !", "rating": 5,
        }, headers=auth(setup["bob_token"]))
        assert res.status_code == 201
        assert res.json["rating"] == 5
        assert res.json["text"] == "Super !"
        assert res.json["user_id"] == setup["bob_id"]
        assert res.json["place_id"] == setup["place_id"]

    def test_create_review_own_place_forbidden(self, client, setup):
        res = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "Mon lieu", "rating": 5,
        }, headers=auth(setup["alice_token"]))
        assert res.status_code == 403

    def test_create_review_duplicate_forbidden(self, client, setup):
        client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "1er avis", "rating": 4,
        }, headers=auth(setup["bob_token"]))
        res = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "2e avis", "rating": 3,
        }, headers=auth(setup["bob_token"]))
        assert res.status_code == 400

    def test_create_review_invalid_rating_too_high(self, client, setup):
        res = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "Test", "rating": 6,
        }, headers=auth(setup["bob_token"]))
        assert res.status_code == 400

    def test_create_review_invalid_rating_zero(self, client, setup):
        res = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "Test", "rating": 0,
        }, headers=auth(setup["bob_token"]))
        assert res.status_code == 400

    def test_create_review_invalid_rating_negative(self, client, setup):
        res = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "Test", "rating": -1,
        }, headers=auth(setup["bob_token"]))
        assert res.status_code == 400

    def test_create_review_place_not_found(self, client, setup):
        res = client.post("/api/v1/reviews/", json={
            "place_id": "00000000-0000-0000-0000-000000000000",
            "text": "Test", "rating": 4,
        }, headers=auth(setup["bob_token"]))
        assert res.status_code == 404

    def test_create_review_no_token(self, client, setup):
        res = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "Test", "rating": 3,
        })
        assert res.status_code == 401

    def test_get_all_reviews_public(self, client, setup):
        client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "Bien", "rating": 4,
        }, headers=auth(setup["bob_token"]))
        res = client.get("/api/v1/reviews/")
        assert res.status_code == 200
        assert len(res.json) == 1

    def test_get_review_by_id(self, client, setup):
        r = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "Bien", "rating": 4,
        }, headers=auth(setup["bob_token"])).json
        res = client.get(f"/api/v1/reviews/{r['id']}")
        assert res.status_code == 200
        assert res.json["id"] == r["id"]

    def test_get_review_not_found(self, client):
        res = client.get("/api/v1/reviews/00000000-0000-0000-0000-000000000000")
        assert res.status_code == 404

    def test_get_reviews_by_place(self, client, setup):
        client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "Bien", "rating": 4,
        }, headers=auth(setup["bob_token"]))
        res = client.get(f"/api/v1/places/{setup['place_id']}/reviews")
        assert res.status_code == 200
        assert len(res.json) == 1

    def test_get_reviews_by_place_not_found(self, client):
        res = client.get("/api/v1/places/00000000-0000-0000-0000-000000000000/reviews")
        assert res.status_code == 404

    def test_update_review_as_author(self, client, setup):
        r = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "Bien", "rating": 4,
        }, headers=auth(setup["bob_token"])).json
        res = client.put(f"/api/v1/reviews/{r['id']}",
                         json={"text": "Très bien", "rating": 5},
                         headers=auth(setup["bob_token"]))
        assert res.status_code == 200
        assert res.json["rating"] == 5
        assert res.json["text"] == "Très bien"

    def test_update_review_as_other_forbidden(self, client, setup):
        r = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "Bien", "rating": 4,
        }, headers=auth(setup["bob_token"])).json
        res = client.put(f"/api/v1/reviews/{r['id']}",
                         json={"text": "Modifié", "rating": 1},
                         headers=auth(setup["alice_token"]))
        assert res.status_code == 403

    def test_update_review_as_admin(self, client, app, setup):
        r = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "Bien", "rating": 4,
        }, headers=auth(setup["bob_token"])).json
        _, admin_token = create_admin(client, app)
        res = client.put(f"/api/v1/reviews/{r['id']}",
                         json={"text": "Modif admin", "rating": 3},
                         headers=auth(admin_token))
        assert res.status_code == 200
        assert res.json["text"] == "Modif admin"

    def test_update_review_not_found(self, client, setup):
        res = client.put("/api/v1/reviews/00000000-0000-0000-0000-000000000000",
                         json={"text": "X", "rating": 3},
                         headers=auth(setup["bob_token"]))
        assert res.status_code == 404

    def test_update_review_no_token(self, client, setup):
        r = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "Bien", "rating": 4,
        }, headers=auth(setup["bob_token"])).json
        res = client.put(f"/api/v1/reviews/{r['id']}",
                         json={"text": "X", "rating": 3})
        assert res.status_code == 401

    def test_delete_review_as_author(self, client, setup):
        r = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "Bien", "rating": 4,
        }, headers=auth(setup["bob_token"])).json
        res = client.delete(f"/api/v1/reviews/{r['id']}",
                            headers=auth(setup["bob_token"]))
        assert res.status_code == 200
        assert client.get(f"/api/v1/reviews/{r['id']}").status_code == 404

    def test_delete_review_as_other_forbidden(self, client, setup):
        r = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "Bien", "rating": 4,
        }, headers=auth(setup["bob_token"])).json
        res = client.delete(f"/api/v1/reviews/{r['id']}",
                            headers=auth(setup["alice_token"]))
        assert res.status_code == 403

    def test_delete_review_as_admin(self, client, app, setup):
        r = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "Bien", "rating": 4,
        }, headers=auth(setup["bob_token"])).json
        _, admin_token = create_admin(client, app)
        res = client.delete(f"/api/v1/reviews/{r['id']}",
                            headers=auth(admin_token))
        assert res.status_code == 200
        assert client.get(f"/api/v1/reviews/{r['id']}").status_code == 404

    def test_delete_review_not_found(self, client, setup):
        res = client.delete("/api/v1/reviews/00000000-0000-0000-0000-000000000000",
                            headers=auth(setup["bob_token"]))
        assert res.status_code == 404

    def test_delete_review_no_token(self, client, setup):
        r = client.post("/api/v1/reviews/", json={
            "place_id": setup["place_id"], "text": "Bien", "rating": 4,
        }, headers=auth(setup["bob_token"])).json
        res = client.delete(f"/api/v1/reviews/{r['id']}")
        assert res.status_code == 401
