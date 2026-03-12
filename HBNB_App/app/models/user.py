import re
from .base_model import BaseModel
from app.extensions import bcrypt


class User(BaseModel):
    """
    Représente un utilisateur de l'application.

    Attributs :
    - first_name / last_name : obligatoires, max 50 caractères
    - email : obligatoire, format valide, unique (géré par la couche persistence)
    - password : haché via bcrypt, jamais exposé en clair
    - is_admin : booléen, False par défaut
    - places : liste des lieux que l'utilisateur possède
    - reviews : liste des avis que l'utilisateur a rédigés
    """

    def __init__(self, first_name: str, last_name: str, email: str,
                 password: str, is_admin: bool = False):
        super().__init__()
        self.first_name = first_name   # setter valide automatiquement
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self._password = None          # stocke le hash, jamais le mot de passe clair
        self.hash_password(password)   # hachage immédiat à la création
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

    # ── Gestion du mot de passe ────────────────────────────────────────
    def hash_password(self, password: str):
        """
        Hache le mot de passe en clair avec bcrypt et le stocke dans _password.
        bcrypt.generate_password_hash() retourne des bytes → decode('utf-8') pour stocker en str.
        """
        if not password or not isinstance(password, str):
            raise ValueError("Le mot de passe est obligatoire.")
        self._password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password: str) -> bool:
        """
        Compare un mot de passe en clair avec le hash stocké.
        Retourne True si correspondance, False sinon.
        Utilisé lors de l'authentification (login).
        """
        return bcrypt.check_password_hash(self._password, password)

    def to_dict(self):
        """
        Sérialise l'utilisateur en dict.
        Le champ 'password' (même haché) n'est JAMAIS inclus :
        il ne doit pas apparaître dans les réponses GET/POST/PUT.
        """
        base = super().to_dict()
        base.update({
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "is_admin": self.is_admin,
        })
        return base
