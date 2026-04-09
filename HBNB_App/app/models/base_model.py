import uuid
from datetime import datetime
from app.extensions import db


class BaseModel(db.Model):
    """
    Classe de base SQLAlchemy pour toutes les entités de l'application.

    __abstract__ = True : SQLAlchemy ne crée PAS de table pour BaseModel lui-même.
    Les sous-classes qui définissent __tablename__ obtiennent leurs propres tables.
    Les sous-classes sans __tablename__ (Place, Review, Amenity) héritent aussi de
    __abstract__ via Python et ne sont pas mappées — elles fonctionnent en mémoire.

    Colonnes communes :
      id         : UUID v4 en string (36 car.), clé primaire
      created_at : datetime UTC à la création
      updated_at : datetime UTC, mis à jour à chaque save()
    """

    __abstract__ = True

    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __init__(self):
        """
        Appelé uniquement pour les NOUVEAUX objets.
        SQLAlchemy ne passe PAS par __init__ lors de la reconstruction depuis la DB
        (utilise __new__ + assignation directe des colonnes depuis les données SQL).
        Les valeurs sont donc aussi gérées par les 'default' des colonnes.
        """
        self.id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def save(self):
        """Met à jour le timestamp 'updated_at' à chaque modification."""
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        """
        Sérialise les champs communs en dict.
        Les datetimes sont convertis en strings ISO 8601 pour les réponses API.
        """
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }