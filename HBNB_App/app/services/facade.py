"""
Facade — Tasks 0-5.

Le Facade est le SEUL point d'entrée entre la couche Présentation (API)
et la couche Business Logic + Persistence.
Il évite que les endpoints Flask connaissent les modèles ou le repository.

Migration vers SQLAlchemy (tâche 5) :
  - self._users utilise désormais SQLAlchemyRepository (persistance DB).
  - Les autres entités (places, reviews, amenities) restent en InMemoryRepository
    en attendant que leurs modèles soient mappés (tâche 6).
"""

from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity
from app.persistence.repository import InMemoryRepository, UserRepository


class HBnBFacade:
    def __init__(self):
        # Users : persistance base de données via SQLAlchemy + get_by_email()
        self._users = UserRepository()

        # Places, Reviews, Amenities : toujours en mémoire
        self._places = InMemoryRepository()
        self._reviews = InMemoryRepository()
        self._amenities = InMemoryRepository()

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
        # Si l'email change, vérifier l'unicité
        if "email" in data:
            existing = self._users.get_by_email(data["email"])
            if existing and existing.id != user_id:
                raise ValueError("Cet email est déjà utilisé par un autre utilisateur.")

        # Le password doit être haché via hash_password(), pas setattr() direct
        # On le traite avant d'appeler le repository générique
        if "password" in data:
            user = self._users.get(user_id)
            if user:
                user.hash_password(data.pop("password"))

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
        # Seuls les champs scalaires du Place sont mis à jour directement.
        # owner_id et amenities nécessitent une résolution d'objets et ne peuvent
        # pas être passés tels quels à setattr (qui attend un objet User/Amenity).
        allowed = {"title", "description", "price", "latitude", "longitude"}
        place_data = {k: v for k, v in data.items() if k in allowed}

        # Si de nouvelles amenities sont fournies, résoudre les UUIDs en objets
        if "amenities" in data:
            place = self._places.get(place_id)
            if place:
                place.amenities = []
                for amenity_id in data["amenities"]:
                    amenity = self._amenities.get(amenity_id)
                    if amenity:
                        place.add_amenity(amenity)

        return self._places.update(place_id, place_data)

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

    def get_review_by_user_and_place(self, user_id: str, place_id: str):
        """
        Retourne la review d'un utilisateur pour un lieu donné, ou None.
        Utilisé pour empêcher les reviews en double.
        """
        for r in self._reviews.get_all():
            if r.user.id == user_id and r.place.id == place_id:
                return r
        return None

    def update_review(self, review_id: str, data: dict) -> Review:
        return self._reviews.update(review_id, data)

    def delete_review(self, review_id: str):
        self._reviews.delete(review_id)
