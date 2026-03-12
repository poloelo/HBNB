import uuid
from datetime import datetime


class BaseModel:
    """
    Classe de base pour toutes les entités de l'application.
    Fournit un identifiant unique (UUID) et les timestamps
    de création/modification automatiques.
    """

    def __init__(self):
        self.id = str(uuid.uuid4())          # Identifiant unique universel
        self.created_at = datetime.utcnow()  # Date de création (UTC)
        self.updated_at = datetime.utcnow()  # Date de dernière modification

    def save(self):
        """Met à jour le timestamp 'updated_at' à chaque modification."""
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        """
        Sérialise l'objet en dictionnaire.
        Convertit les datetimes en strings ISO 8601 pour les réponses API.
        """
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
