from sqlalchemy.orm import validates
from .base_model import BaseModel
from app.extensions import db


class Place(BaseModel):
    """
    Représente un lieu à louer dans l'application — mappé SQLAlchemy.

    Table 'places' : colonnes id/created_at/updated_at héritées de BaseModel.
    Colonnes propres :
    - title       : obligatoire, max 100 caractères
    - description : optionnel
    - price       : obligatoire, float > 0
    - latitude    : float entre -90 et 90
    - longitude   : float entre -180 et 180
    - owner_id    : UUID du propriétaire (String, sans FK pour l'instant)

    Les relations (owner, amenities, reviews) seront ajoutées dans une tâche ultérieure.
    """

    __tablename__ = 'places'

    title       = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1024), nullable=True, default="")
    price       = db.Column(db.Float, nullable=False)
    latitude    = db.Column(db.Float, nullable=False)
    longitude   = db.Column(db.Float, nullable=False)
    owner_id    = db.Column(db.String(36), nullable=False)

    def __init__(self, title: str, price: float, latitude: float,
                 longitude: float, owner_id: str, description: str = ""):
        super().__init__()
        self.title       = title
        self.description = description
        self.price       = price
        self.latitude    = latitude
        self.longitude   = longitude
        self.owner_id    = owner_id

    # ── Validation via SQLAlchemy @validates ───────────────────────────────────

    @validates('title')
    def validate_title(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("title est obligatoire.")
        if len(value) > 100:
            raise ValueError("title ne doit pas dépasser 100 caractères.")
        return value

    @validates('price')
    def validate_price(self, key, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("price doit être un nombre.")
        if value <= 0:
            raise ValueError("price doit être strictement positif.")
        return value

    @validates('latitude')
    def validate_latitude(self, key, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("latitude doit être un nombre.")
        if not (-90.0 <= value <= 90.0):
            raise ValueError("latitude doit être comprise entre -90 et 90.")
        return value

    @validates('longitude')
    def validate_longitude(self, key, value):
        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError("longitude doit être un nombre.")
        if not (-180.0 <= value <= 180.0):
            raise ValueError("longitude doit être comprise entre -180 et 180.")
        return value

    @validates('owner_id')
    def validate_owner_id(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("owner_id est obligatoire.")
        return value

    def to_dict(self):
        base = super().to_dict()
        base.update({
            "title":       self.title,
            "description": self.description,
            "price":       self.price,
            "latitude":    self.latitude,
            "longitude":   self.longitude,
            "owner_id":    self.owner_id,
        })
        return base
