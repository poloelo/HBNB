"""
Facade (Task 0 + Task 1).

Le Facade est le SEUL point d'entrée entre la couche Présentation (API)
et la couche Business Logic + Persistence.
Il évite que les endpoints Flask connaissent les modèles ou le repository.
"""

from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity
from app.persistence.repository import InMemoryRepository


class HBnBFacade:
    def __init__(self):
        self._users = InMemoryRepository()
        self._places = InMemoryRepository()
        self._reviews = InMemoryRepository()
        self._amenities = InMemoryRepository()

    # ══════════════════════════════════════════════════
    #  USERS
    # ══════════════════════════════════════════════════
    def create_user(self, data: dict) -> User:
        if self._users.get_by_attribute("email", data.get("email")):
            raise ValueError("Un utilisateur avec cet email existe déjà.")
        user = User(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            is_admin=data.get("is_admin", False),
        )
        self._users.add(user)
        return user

    def get_user(self, user_id: str) -> User:
        return self._users.get(user_id)

    def get_all_users(self) -> list:
        return self._users.get_all()

    def update_user(self, user_id: str, data: dict) -> User:
        # Si l'email change, vérifier l'unicité
        if "email" in data:
            existing = self._users.get_by_attribute("email", data["email"])
            if existing and existing.id != user_id:
                raise ValueError("Cet email est déjà utilisé par un autre utilisateur.")
        return self._users.update(user_id, data)

    # ══════════════════════════════════════════════════
    #  AMENITIES
    # ══════════════════════════════════════════════════
    def create_amenity(self, data: dict) -> Amenity:
        amenity = Amenity(name=data["name"])
        self._amenities.add(amenity)
        return amenity

    def get_amenity(self, amenity_id: str) -> Amenity:
        return self._amenities.get(amenity_id)

    def get_all_amenities(self) -> list:
        return self._amenities.get_all()

    def update_amenity(self, amenity_id: str, data: dict) -> Amenity:
        return self._amenities.update(amenity_id, data)

    # ══════════════════════════════════════════════════
    #  PLACES
    # ══════════════════════════════════════════════════
    def create_place(self, data: dict) -> Place:
        owner = self._users.get(data["owner_id"])
        if not owner:
            raise ValueError(f"Propriétaire introuvable : {data['owner_id']}")
        place = Place(
            title=data["title"],
            price=data["price"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            owner=owner,
            description=data.get("description", ""),
        )
        # Ajout optionnel des amenities à la création
        for amenity_id in data.get("amenities", []):
            amenity = self._amenities.get(amenity_id)
            if amenity:
                place.add_amenity(amenity)
        self._places.add(place)
        return place

    def get_place(self, place_id: str) -> Place:
        return self._places.get(place_id)

    def get_all_places(self) -> list:
        return self._places.get_all()

    def update_place(self, place_id: str, data: dict) -> Place:
        return self._places.update(place_id, data)

    # ══════════════════════════════════════════════════
    #  REVIEWS
    # ══════════════════════════════════════════════════
    def create_review(self, data: dict) -> Review:
        place = self._places.get(data["place_id"])
        if not place:
            raise ValueError(f"Lieu introuvable : {data['place_id']}")
        user = self._users.get(data["user_id"])
        if not user:
            raise ValueError(f"Utilisateur introuvable : {data['user_id']}")
        review = Review(
            text=data["text"],
            rating=data["rating"],
            place=place,
            user=user,
        )
        self._reviews.add(review)
        return review

    def get_review(self, review_id: str) -> Review:
        return self._reviews.get(review_id)

    def get_all_reviews(self) -> list:
        return self._reviews.get_all()

    def get_reviews_by_place(self, place_id: str) -> list:
        return [r for r in self._reviews.get_all() if r.place.id == place_id]

    def update_review(self, review_id: str, data: dict) -> Review:
        return self._reviews.update(review_id, data)

    def delete_review(self, review_id: str):
        self._reviews.delete(review_id)
