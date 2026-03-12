from .base_model import BaseModel


class Review(BaseModel):
    """
    Représente un avis laissé par un utilisateur sur un lieu.

    Attributs :
    - text   : obligatoire, contenu de l'avis
    - rating : entier entre 1 et 5
    - place  : instance Place — relation many-to-one
    - user   : instance User — relation many-to-one
    """

    def __init__(self, text: str, rating: int, place, user):
        super().__init__()
        self.text = text
        self.rating = rating
        self.place = place   # objet Place complet
        self.user = user     # objet User complet

        # Relations bidirectionnelles : la place et l'user gardent leurs reviews
        place.add_review(self)
        user.reviews.append(self)

    # ── text ───────────────────────────────────────────────────────────────
    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("text est obligatoire et doit être une chaîne.")
        self._text = value

    # ── rating ─────────────────────────────────────────────────────────────
    @property
    def rating(self):
        return self._rating

    @rating.setter
    def rating(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError("rating doit être un entier.")
        if not (1 <= value <= 5):
            raise ValueError("rating doit être compris entre 1 et 5.")
        self._rating = value

    def to_dict(self):
        base = super().to_dict()
        base.update({
            "text": self.text,
            "rating": self.rating,
            # On expose les infos clés de la place et de l'auteur directement
            "place_id": self.place.id,
            "user": {
                "id": self.user.id,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
            },
        })
        return base
