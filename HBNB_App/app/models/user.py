import re
from .base_model import BaseModel


class User(BaseModel):
    """
    Représente un utilisateur de l'application.

    Attributs :
    - first_name / last_name : obligatoires, max 50 caractères
    - email : obligatoire, format valide, unique (géré par la couche persistence)
    - is_admin : booléen, False par défaut
    - places : liste des lieux que l'utilisateur possède
    - reviews : liste des avis que l'utilisateur a rédigés
    """

    def __init__(self, first_name: str, last_name: str, email: str, is_admin: bool = False):
        super().__init__()
        self.first_name = first_name   # setter valide automatiquement
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.places = []   # relation 1-to-many : un user possède plusieurs places
        self.reviews = []  # relation 1-to-many : un user écrit plusieurs reviews

    # ── Validation first_name ──────────────────────────────────────────────
    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("first_name est obligatoire et doit être une chaîne.")
        if len(value) > 50:
            raise ValueError("first_name ne doit pas dépasser 50 caractères.")
        self._first_name = value

    # ── Validation last_name ───────────────────────────────────────────────
    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("last_name est obligatoire et doit être une chaîne.")
        if len(value) > 50:
            raise ValueError("last_name ne doit pas dépasser 50 caractères.")
        self._last_name = value

    # ── Validation email ───────────────────────────────────────────────────
    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("email est obligatoire.")
        # Regex simple mais suffisante pour valider un format d'email
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not re.match(pattern, value):
            raise ValueError(f"Format d'email invalide : {value}")
        self._email = value

    def to_dict(self):
        base = super().to_dict()
        base.update({
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "is_admin": self.is_admin,
        })
        return base
