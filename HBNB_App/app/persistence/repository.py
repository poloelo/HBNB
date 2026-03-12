"""
Persistence layer — Repository pattern.

Deux implémentations de la même interface :
  - InMemoryRepository  : stockage dict Python (utilisé pour Places, Reviews, Amenities)
  - SQLAlchemyRepository: stockage base de données via SQLAlchemy (utilisé pour Users)

Les deux exposent exactement les mêmes méthodes, ce qui permet à la Facade
de les utiliser de façon interchangeable sans connaître le backend.

NOTE : SQLAlchemyRepository nécessite que les modèles soient mappés avec
SQLAlchemy (db.Model). Ce mapping est réalisé dans la tâche suivante.
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
