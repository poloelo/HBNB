"""
Persistence layer — Repository pattern.

Deux implémentations de la même interface :
  - InMemoryRepository  : stockage dict Python
  - SQLAlchemyRepository: stockage base de données via SQLAlchemy

Les deux exposent exactement les mêmes méthodes, ce qui permet à la Facade
de les utiliser de façon interchangeable sans connaître le backend.

Repositories spécialisés :
  - UserRepository    : ajoute get_by_email()
  - PlaceRepository   : wrapper SQLAlchemy pour Place
  - ReviewRepository  : ajoute get_by_place_id() et get_by_user_and_place()
  - AmenityRepository : wrapper SQLAlchemy pour Amenity
"""

from typing import Optional
from app.models.base_model import BaseModel
from app.extensions import db



# ══════════════════════════════════════════════════════════════════════════════
#  InMemoryRepository — backend dict Python
# ══════════════════════════════════════════════════════════════════════════════

class InMemoryRepository:
    """
    Stockage en mémoire via un dictionnaire Python.
    Utilisé pour Places, Reviews et Amenities (pas encore migrés vers DB).
    Toutes les données sont perdues au redémarrage du serveur.
    """

    def __init__(self):
        self._storage = {}

    def add(self, obj: BaseModel) -> None:
        if obj.id in self._storage:
            raise ValueError("Object already exists")
        self._storage[obj.id] = obj

    def get(self, id: str) -> Optional[BaseModel]:
        return self._storage.get(id)

    def update(self, obj_id: str, data: dict):
        obj = self._storage.get(obj_id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            obj.save()
        return obj

    def get_all(self) -> list:
        return list(self._storage.values())

    def delete(self, obj_id: str) -> None:
        self._storage.pop(obj_id, None)

    def get_by_attribute(self, attr: str, value):
        return next(
            (o for o in self._storage.values() if getattr(o, attr, None) == value),
            None
        )


# ══════════════════════════════════════════════════════════════════════════════
#  SQLAlchemyRepository — backend base de données
# ══════════════════════════════════════════════════════════════════════════════

class SQLAlchemyRepository:
    """
    Repository SQLAlchemy — implémente la même interface qu'InMemoryRepository.

    Reçoit la classe du modèle SQLAlchemy en paramètre (ex: SQLAlchemyRepository(User)).
    Toutes les opérations passent par db.session pour la persistance.

    Prérequis : le modèle doit hériter de db.Model (mapping SQLAlchemy).
    Ce mapping est réalisé dans la tâche 6 (SQLAlchemy Model Mapping).
    """

    def __init__(self, model):
        """
        :param model: Classe SQLAlchemy mappée (ex: User, Place, Review, Amenity)
        """
        self.model = model

    def add(self, obj) -> None:
        """
        Ajoute un objet en base de données.
        db.session.add() + db.session.commit() rendent la transaction permanente.
        """
        db.session.add(obj)
        db.session.commit()

    def get(self, id: str):
        """
        Récupère un objet par sa clé primaire (id UUID).
        db.session.get() est la méthode recommandée par SQLAlchemy 2.0+
        (remplace Model.query.get() déprécié).
        """
        return db.session.get(self.model, id)

    def update(self, obj_id: str, data: dict):
        """
        Met à jour un objet existant.
        setattr() modifie les attributs, puis commit() persiste les changements.
        obj.save() met à jour le champ updated_at (défini dans BaseModel).
        """
        obj = self.get(obj_id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            obj.save()
            db.session.commit()
        return obj

    def get_all(self) -> list:
        """
        Retourne tous les enregistrements de la table.
        db.session.execute(db.select(Model)) est la syntaxe SQLAlchemy 2.0.
        """
        return db.session.execute(db.select(self.model)).scalars().all()

    def delete(self, obj_id: str) -> None:
        """
        Supprime un enregistrement par son id.
        db.session.delete() + commit() rendent la suppression permanente.
        """
        obj = self.get(obj_id)
        if obj:
            db.session.delete(obj)
            db.session.commit()

    def get_by_attribute(self, attr: str, value):
        """
        Filtre par un attribut donné et retourne le premier résultat.
        db.select().where() génère une requête SQL WHERE attr = value.
        """
        return db.session.execute(
            db.select(self.model).where(getattr(self.model, attr) == value)
        ).scalars().first()


# ══════════════════════════════════════════════════════════════════════════════
#  UserRepository — spécialisation pour la colonne email
# ══════════════════════════════════════════════════════════════════════════════

class UserRepository(SQLAlchemyRepository):
    """
    Repository spécialisé pour User.

    Hérite de SQLAlchemyRepository et ajoute get_by_email() qui interroge
    directement la colonne 'email' du modèle User via SQLAlchemy.
    On importe User ici (import tardif) pour éviter les imports circulaires
    au niveau du module.
    """

    def __init__(self):
        from app.models.user import User
        super().__init__(User)

    def get_by_email(self, email: str):
        """
        Retourne l'utilisateur correspondant à l'email donné, ou None.
        Utilisé par la Facade pour l'authentification et la vérification d'unicité.
        """
        return db.session.execute(
            db.select(self.model).where(self.model.email == email)
        ).scalars().first()


# ══════════════════════════════════════════════════════════════════════════════
#  PlaceRepository
# ══════════════════════════════════════════════════════════════════════════════

class PlaceRepository(SQLAlchemyRepository):
    """Repository SQLAlchemy pour le modèle Place."""

    def __init__(self):
        from app.models.place import Place
        super().__init__(Place)


# ══════════════════════════════════════════════════════════════════════════════
#  ReviewRepository
# ══════════════════════════════════════════════════════════════════════════════

class ReviewRepository(SQLAlchemyRepository):
    """
    Repository SQLAlchemy pour le modèle Review.

    Méthodes supplémentaires :
    - get_by_place_id()       : retourne tous les avis d'un lieu
    - get_by_user_and_place() : retourne l'avis d'un utilisateur pour un lieu
    """

    def __init__(self):
        from app.models.review import Review
        super().__init__(Review)

    def get_by_place_id(self, place_id: str) -> list:
        """Retourne tous les avis associés à un lieu donné."""
        return db.session.execute(
            db.select(self.model).where(self.model.place_id == place_id)
        ).scalars().all()

    def get_by_user_and_place(self, user_id: str, place_id: str):
        """Retourne l'avis d'un utilisateur pour un lieu, ou None."""
        return db.session.execute(
            db.select(self.model).where(
                self.model.user_id == user_id,
                self.model.place_id == place_id
            )
        ).scalars().first()


# ══════════════════════════════════════════════════════════════════════════════
#  AmenityRepository
# ══════════════════════════════════════════════════════════════════════════════

class AmenityRepository(SQLAlchemyRepository):
    """Repository SQLAlchemy pour le modèle Amenity."""

    def __init__(self):
        from app.models.amenity import Amenity
        super().__init__(Amenity)