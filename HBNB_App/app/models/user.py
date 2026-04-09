import re
from sqlalchemy.orm import validates, relationship
from .base_model import BaseModel
from app.extensions import bcrypt, db


class User(BaseModel):
    """
    Représente un utilisateur de l'application — mappé SQLAlchemy.

    Table 'users' : colonnes id/created_at/updated_at héritées de BaseModel.
    Colonnes propres :
    - first_name / last_name : obligatoires, max 50 caractères
    - email      : obligatoire, format valide, unique en base
    - password   : stocké haché (bcrypt), jamais exposé en clair
    - is_admin   : booléen, False par défaut

    Relations :
    - places  : one-to-many → Place  (back_populates='owner',  cascade delete)
    - reviews : one-to-many → Review (back_populates='user',   cascade delete)

    La validation passe par les décorateurs @validates de SQLAlchemy,
    déclenchés automatiquement à chaque assignation de colonne.
    """

    __tablename__ = 'users'

    first_name = db.Column(db.String(50),  nullable=False)
    last_name  = db.Column(db.String(50),  nullable=False)
    email      = db.Column(db.String(120), nullable=False, unique=True)
    # Colonne DB nommée 'password', accessible en Python via self._password
    _password  = db.Column('password', db.String(128), nullable=False)
    is_admin   = db.Column(db.Boolean, nullable=False, default=False)

    # ── Relations ──────────────────────────────────────────────────────────────
    places  = relationship(
        'Place',
        back_populates='owner',
        lazy='select',
        cascade='all, delete-orphan'
    )
    reviews = relationship(
        'Review',
        back_populates='user',
        lazy='select',
        cascade='all, delete-orphan'
    )

    def __init__(self, first_name: str, last_name: str, email: str,
                 password: str, is_admin: bool = False):
        super().__init__()
        self.first_name = first_name
        self.last_name  = last_name
        self.email      = email
        self.is_admin   = is_admin
        self._password  = None          # initialisé avant le hachage
        self.hash_password(password)    # hachage immédiat

    # ── Validation via SQLAlchemy @validates ───────────────────────────────────
    # @validates est déclenché par SQLAlchemy à chaque setattr sur la colonne,
    # y compris lors des mises à jour via le repository.

    @validates('first_name')
    def validate_first_name(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("first_name est obligatoire et doit être une chaîne.")
        if len(value) > 50:
            raise ValueError("first_name ne doit pas dépasser 50 caractères.")
        return value

    @validates('last_name')
    def validate_last_name(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("last_name est obligatoire et doit être une chaîne.")
        if len(value) > 50:
            raise ValueError("last_name ne doit pas dépasser 50 caractères.")
        return value

    @validates('email')
    def validate_email(self, key, value):
        if not value or not isinstance(value, str):
            raise ValueError("email est obligatoire.")
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not re.match(pattern, value):
            raise ValueError(f"Format d'email invalide : {value}")
        return value

    # ── Gestion du mot de passe ────────────────────────────────────────────────

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
        Le champ 'password' (même haché) n'est JAMAIS inclus dans la réponse API.
        """
        base = super().to_dict()
        base.update({
            "first_name": self.first_name,
            "last_name":  self.last_name,
            "email":      self.email,
            "is_admin":   self.is_admin,
        })
        return base