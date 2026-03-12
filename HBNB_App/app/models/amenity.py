from .base_model import BaseModel


class Amenity(BaseModel):
    """
    Représente un équipement/service disponible dans un lieu.
    Exemples : Wi-Fi, piscine, parking, climatisation...

    Attributs :
    - name : obligatoire, max 50 caractères
    """

    def __init__(self, name: str):
        super().__init__()
        self.name = name  # setter valide

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("name est obligatoire et doit être une chaîne.")
        if len(value) > 50:
            raise ValueError("name ne doit pas dépasser 50 caractères.")
        self._name = value

    def to_dict(self):
        base = super().to_dict()
        base.update({"name": self.name})
        return base
