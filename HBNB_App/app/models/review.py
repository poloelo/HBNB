from sqlalchemy.orm import validates
from .base_model import BaseModel
from app.extensions import db


class Review(BaseModel):
    """
    Représente un avis laissé par un utilisateur sur un lieu — mappé SQLAlchemy.

    Table 'reviews' : colonnes id/created_at/updated_at héritées de BaseModel.
    Colonnes propres :
    - text     : obligatoire, contenu de l'avis
    - rating   : entier entre 1 et 5
    - place_id : UUID du lieu (String, sans FK pour l'instant)
    - user_id  : UUID de l'auteur (String, sans FK pour l'instant)

    Les relations (place, user) seront ajoutées dans une tâche ultérieure.
    """

    __tablename__ = 'reviews'

    text     = db.Column(db.String(2048), nullable=False)
    rating   = db.Column(db.Integer, nullable=False)
    place_id = db.Column(db.String(36), nullable=False)
    user_id  = db.Column(db.String(36), nullable=False)

    def __init__(self, text: str, rating: int, place_id: str, user_id: str):
        super().__init__()
        self.text     = text
        self.rating   = rating
        self.place_id = place_id
        self.user_id  = user_id

    # ── Validation via SQLAlchemy @validates ───────────────────────────────────

    @validates('text')
    def validate_text(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("text est obligatoire et doit être une chaîne.")
        return value

    @validates('rating')
    def validate_rating(self, key, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError("rating doit être un entier.")
        if not (1 <= value <= 5):
            raise ValueError("rating doit être compris entre 1 et 5.")
        return value

    @validates('place_id')
    def validate_place_id(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("place_id est obligatoire.")
        return value

    @validates('user_id')
    def validate_user_id(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("user_id est obligatoire.")
        return value

    def to_dict(self):
        base = super().to_dict()
        base.update({
            "text":     self.text,
            "rating":   self.rating,
            "place_id": self.place_id,
            "user_id":  self.user_id,
        })
        return base
