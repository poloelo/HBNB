from .base_model import BaseModel


class Place(BaseModel):
    """
    Représente un lieu à louer dans l'application.

    Attributs :
    - title          : obligatoire, max 100 caractères
    - description    : optionnel
    - price          : obligatoire, float > 0
    - latitude       : float entre -90 et 90
    - longitude      : float entre -180 et 180
    - owner          : instance User — relation many-to-one (un lieu a 1 propriétaire)
    - amenities      : liste d'instances Amenity — relation many-to-many
    - reviews        : liste d'instances Review — relation 1-to-many
    """

    def __init__(self, title: str, price: float, latitude: float,
                 longitude: float, owner, description: str = ""):
        super().__init__()
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner        # objet User complet (pas juste l'id)
        self.amenities = []       # liste d'objets Amenity
        self.reviews = []         # liste d'objets Review

        # L'owner tient aussi une référence vers ses places (relation bidirectionnelle)
        owner.places.append(self)

    # ── title ──────────────────────────────────────────────────────────────
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("title est obligatoire.")
        if len(value) > 100:
            raise ValueError("title ne doit pas dépasser 100 caractères.")
        self._title = value

    # ── price ──────────────────────────────────────────────────────────────
    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("price doit être un nombre.")
        if value <= 0:
            raise ValueError("price doit être strictement positif.")
        self._price = value

    # ── latitude ───────────────────────────────────────────────────────────
    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("latitude doit être un nombre.")
        if not (-90.0 <= value <= 90.0):
            raise ValueError("latitude doit être comprise entre -90 et 90.")
        self._latitude = value

    # ── longitude ──────────────────────────────────────────────────────────
    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("longitude doit être un nombre.")
        if not (-180.0 <= value <= 180.0):
            raise ValueError("longitude doit être comprise entre -180 et 180.")
        self._longitude = value

    # ── Méthodes utilitaires ───────────────────────────────────────────────
    def add_amenity(self, amenity):
        """Ajoute un équipement si pas déjà présent."""
        if amenity not in self.amenities:
            self.amenities.append(amenity)

    def add_review(self, review):
        """Ajoute un avis (appelé automatiquement par Review.__init__)."""
        if review not in self.reviews:
            self.reviews.append(review)

    def to_dict(self):
        base = super().to_dict()
        base.update({
            "title": self.title,
            "description": self.description,
            "price": self.price,
            "latitude": self.latitude,
            "longitude": self.longitude,
            # On retourne les infos du propriétaire directement (pas juste l'id)
            # pour que l'API puisse exposer first_name, last_name sans requête supplémentaire
            "owner": {
                "id": self.owner.id,
                "first_name": self.owner.first_name,
                "last_name": self.owner.last_name,
                "email": self.owner.email,
            },
            "amenities": [a.to_dict() for a in self.amenities],
        })
        return base
