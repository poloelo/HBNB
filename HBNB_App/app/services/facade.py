"""
Facade — couche service unique entre l'API et la persistence.

Le Facade est le SEUL point d'entrée entre la couche Présentation (API)
et la couche Business Logic + Persistence.
Il évite que les endpoints Flask connaissent les modèles ou le repository.

Tous les modèles (User, Place, Review, Amenity) sont désormais mappés
SQLAlchemy et utilisent leur repository dédié.
"""

from app.persistence.repository import (
    UserRepository,
    PlaceRepository,
    ReviewRepository,
    AmenityRepository,
)


class HBnBFacade:
    def __init__(self):
        self._users     = UserRepository()
        self._places    = PlaceRepository()
        self._reviews   = ReviewRepository()
        self._amenities = AmenityRepository()

    # ══════════════════════════════════════════════════
    #  USERS
    # ══════════════════════════════════════════════════
    def create_user(self, data: dict):
        if self._users.get_by_email(data.get("email")):
            raise ValueError("Un utilisateur avec cet email existe déjà.")
        from app.models.user import User
        user = User(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password=data["password"],
            is_admin=data.get("is_admin", False),
        )
        self._users.add(user)
        return user

    def get_user(self, user_id: str):
        return self._users.get(user_id)

    def get_user_by_email(self, email: str):
        """Récupère un utilisateur par son email. Utilisé pour l'authentification."""
        return self._users.get_by_email(email)

    def get_all_users(self) -> list:
        return self._users.get_all()

    def update_user(self, user_id: str, data: dict):
        if "email" in data:
            existing = self._users.get_by_email(data["email"])
            if existing and existing.id != user_id:
                raise ValueError("Cet email est déjà utilisé par un autre utilisateur.")

        if "password" in data:
            user = self._users.get(user_id)
            if user:
                user.hash_password(data.pop("password"))

        return self._users.update(user_id, data)

    # ══════════════════════════════════════════════════
    #  AMENITIES
    # ══════════════════════════════════════════════════
    def create_amenity(self, data: dict):
        from app.models.amenity import Amenity
        amenity = Amenity(name=data["name"])
        self._amenities.add(amenity)
        return amenity

    def get_amenity(self, amenity_id: str):
        return self._amenities.get(amenity_id)

    def get_all_amenities(self) -> list:
        return self._amenities.get_all()

    def update_amenity(self, amenity_id: str, data: dict):
        return self._amenities.update(amenity_id, data)

    # ══════════════════════════════════════════════════
    #  PLACES
    # ══════════════════════════════════════════════════
    def create_place(self, data: dict):
        # Valider que le propriétaire existe
        owner = self._users.get(data["owner_id"])
        if not owner:
            raise ValueError(f"Propriétaire introuvable : {data['owner_id']}")

        from app.models.place import Place
        place = Place(
            title=data["title"],
            price=data["price"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            owner_id=data["owner_id"],
            description=data.get("description", ""),
        )

        # Liaison des amenities via la relation many-to-many
        for amenity_id in data.get("amenities", []):
            amenity = self._amenities.get(amenity_id)
            if amenity:
                place.add_amenity(amenity)

        self._places.add(place)
        return place

    def get_place(self, place_id: str):
        return self._places.get(place_id)

    def get_all_places(self) -> list:
        return self._places.get_all()

    def update_place(self, place_id: str, data: dict):
        return self._places.update(place_id, data)

    # ══════════════════════════════════════════════════
    #  REVIEWS
    # ══════════════════════════════════════════════════
    def create_review(self, data: dict):
        # Valider que le lieu et l'utilisateur existent
        place = self._places.get(data["place_id"])
        if not place:
            raise ValueError(f"Lieu introuvable : {data['place_id']}")
        user = self._users.get(data["user_id"])
        if not user:
            raise ValueError(f"Utilisateur introuvable : {data['user_id']}")

        from app.models.review import Review
        review = Review(
            text=data["text"],
            rating=data["rating"],
            place_id=data["place_id"],
            user_id=data["user_id"],
        )
        self._reviews.add(review)
        return review

    def get_review(self, review_id: str):
        return self._reviews.get(review_id)

    def get_all_reviews(self) -> list:
        return self._reviews.get_all()

    def get_reviews_by_place(self, place_id: str) -> list:
        return self._reviews.get_by_place_id(place_id)

    def get_review_by_user_and_place(self, user_id: str, place_id: str):
        """
        Retourne la review d'un utilisateur pour un lieu donné, ou None.
        Utilisé pour empêcher les reviews en double.
        """
        return self._reviews.get_by_user_and_place(user_id, place_id)

    def update_review(self, review_id: str, data: dict):
        return self._reviews.update(review_id, data)

    def delete_review(self, review_id: str):
        self._reviews.delete(review_id)