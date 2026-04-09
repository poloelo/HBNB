from sqlalchemy.orm import validates, relationship
from .base_model import BaseModel
from app.extensions import db


# ── Table d'association many-to-many Place ↔ Amenity ──────────────────────────
# Pas de modèle dédié : SQLAlchemy gère directement la table pivot.
place_amenity = db.Table(
    'place_amenity',
    db.Column(
        'place_id',
        db.String(36),
        db.ForeignKey('places.id'),
        primary_key=True
    ),
    db.Column(
        'amenity_id',
        db.String(36),
        db.ForeignKey('amenities.id'),
        primary_key=True
    )
)


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
    - owner_id    : FK → users.id

    Relations :
    - owner     : many-to-one → User  (back_populates='places')
    - reviews   : one-to-many → Review (back_populates='place', cascade delete)
    - amenities : many-to-many ↔ Amenity (via place_amenity, backref='places')
    """

    __tablename__ = 'places'

    title       = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1024), nullable=True, default="")
    price       = db.Column(db.Float, nullable=False)
    latitude    = db.Column(db.Float, nullable=False)
    longitude   = db.Column(db.Float, nullable=False)
    owner_id    = db.Column(
        db.String(36),
        db.ForeignKey('users.id'),
        nullable=False
    )

    # ── Relations ──────────────────────────────────────────────────────────────
    owner = relationship(
        'User',
        back_populates='places'
    )
    reviews = relationship(
        'Review',
        back_populates='place',
        lazy='select',
        cascade='all, delete-orphan'
    )
    amenities = relationship(
        'Amenity',
        secondary=place_amenity,
        lazy='select',
        backref=db.backref('places', lazy='select')
    )

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

    # ── Méthodes utilitaires ───────────────────────────────────────────────────

    def add_amenity(self, amenity):
        """Lie un équipement à ce lieu (many-to-many via place_amenity)."""
        if amenity not in self.amenities:
            self.amenities.append(amenity)

    def to_dict(self):
        base = super().to_dict()
        base.update({
            "title":       self.title,
            "description": self.description,
            "price":       self.price,
            "latitude":    self.latitude,
            "longitude":   self.longitude,
            "owner_id":    self.owner_id,
            "owner": {
                "id":         self.owner.id,
                "first_name": self.owner.first_name,
                "last_name":  self.owner.last_name,
                "email":      self.owner.email,
            } if self.owner else None,
            "amenities":   [{"id": a.id, "name": a.name} for a in self.amenities],
        })
        return base