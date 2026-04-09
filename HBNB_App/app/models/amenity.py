from sqlalchemy.orm import validates
from .base_model import BaseModel
from app.extensions import db


class Amenity(BaseModel):
    """
    Représente un équipement/service disponible dans un lieu — mappé SQLAlchemy.

    Table 'amenities' : colonnes id/created_at/updated_at héritées de BaseModel.
    Colonnes propres :
    - name : obligatoire, max 50 caractères
    """

    __tablename__ = 'amenities'

    name = db.Column(db.String(50), nullable=False)

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    @validates('name')
    def validate_name(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("name est obligatoire et doit être une chaîne.")
        if len(value) > 50:
            raise ValueError("name ne doit pas dépasser 50 caractères.")
        return value

    def to_dict(self):
        base = super().to_dict()
        base.update({"name": self.name})
        return base