"""
Place Endpoints — Task 4
========================
Routes disponibles :
  POST   /api/v1/places/       → créer un lieu
  GET    /api/v1/places/       → lister tous les lieux
  GET    /api/v1/places/<id>   → récupérer un lieu par id (avec owner + amenities)
  PUT    /api/v1/places/<id>   → mettre à jour un lieu

DELETE n'est PAS implémenté dans cette partie.
"""

from flask_restx import Namespace, Resource, fields
from app.services import facade

# ── Namespace ──────────────────────────────────────────────────────────────────
api = Namespace("places", description="Opérations sur les lieux")

# ── Sous-modèles imbriqués (pour la réponse enrichie) ─────────────────────────
owner_model = api.model(
    "Owner",
    {
        "id":         fields.String(description="UUID du propriétaire"),
        "first_name": fields.String(description="Prénom"),
        "last_name":  fields.String(description="Nom"),
        "email":      fields.String(description="Email"),
    },
)

amenity_nested_model = api.model(
    "AmenityNested",
    {
        "id":   fields.String(description="UUID de l'amenity"),
        "name": fields.String(description="Nom de l'amenity"),
    },
)

# ── Modèle d'entrée (création / mise à jour) ───────────────────────────────────
place_model = api.model(
    "Place",
    {
        "title":       fields.String(required=True,  description="Titre du lieu (max 100 car.)"),
        "description": fields.String(required=False, description="Description détaillée"),
        "price":       fields.Float(required=True,   description="Prix par nuit (> 0)"),
        "latitude":    fields.Float(required=True,   description="Latitude entre -90 et 90"),
        "longitude":   fields.Float(required=True,   description="Longitude entre -180 et 180"),
        "owner_id":    fields.String(required=True,  description="UUID du propriétaire (User)"),
        "amenities":   fields.List(fields.String,    required=False,
                                   description="Liste d'UUIDs d'amenities"),
    },
)

# ── Modèle de réponse enrichi ──────────────────────────────────────────────────
place_response_model = api.model(
    "PlaceResponse",
    {
        "id":          fields.String(description="UUID unique"),
        "title":       fields.String(description="Titre"),
        "description": fields.String(description="Description"),
        "price":       fields.Float(description="Prix par nuit"),
        "latitude":    fields.Float(description="Latitude"),
        "longitude":   fields.Float(description="Longitude"),
        "owner":       fields.Nested(owner_model,           description="Infos du propriétaire"),
        "amenities":   fields.List(fields.Nested(amenity_nested_model),
                                   description="Équipements disponibles"),
        "created_at":  fields.String(description="Date de création ISO 8601"),
        "updated_at":  fields.String(description="Date de mise à jour ISO 8601"),
    },
)

# ── Modèle de réponse allégé pour la liste ─────────────────────────────────────
# (évite d'envoyer l'objet owner complet dans une liste de 100 lieux)
place_list_model = api.model(
    "PlaceList",
    {
        "id":        fields.String(description="UUID unique"),
        "title":     fields.String(description="Titre"),
        "price":     fields.Float(description="Prix par nuit"),
        "latitude":  fields.Float(description="Latitude"),
        "longitude": fields.Float(description="Longitude"),
    },
)


# ── /api/v1/places/ ────────────────────────────────────────────────────────────
@api.route("/")
class PlaceList(Resource):
    """Collection de lieux."""

    @api.marshal_list_with(place_list_model)
    def get(self):
        """
        GET /api/v1/places/
        Retourne la liste résumée de tous les lieux.
        Réponse 200 : liste JSON (id, title, price, lat, lng).
        """
        places = facade.get_all_places()
        return [p.to_dict() for p in places], 200

    @api.expect(place_model, validate=True)
    @api.marshal_with(place_response_model, code=201)
    def post(self):
        """
        POST /api/v1/places/
        Crée un nouveau lieu.

        Body attendu : { "title": "...", "price": 80, "latitude": 48.85,
                         "longitude": 2.35, "owner_id": "<uuid>", "amenities": [] }
        Réponse 201 : le lieu créé avec owner et amenities.
        Réponse 400 : champ invalide (price <= 0, lat hors range...) ou owner introuvable.
        """
        try:
            place = facade.create_place(api.payload)
        except (ValueError, KeyError) as e:
            api.abort(400, str(e))

        return place.to_dict(), 201


# ── /api/v1/places/<place_id> ──────────────────────────────────────────────────
@api.route("/<string:place_id>")
@api.param("place_id", "L'identifiant UUID du lieu")
class PlaceResource(Resource):
    """Ressource individuelle d'un lieu."""

    @api.marshal_with(place_response_model)
    def get(self, place_id):
        """
        GET /api/v1/places/<place_id>
        Retourne un lieu avec les infos complètes du propriétaire et des amenities.
        Réponse 200 : le lieu trouvé.
        Réponse 404 : si l'id n'existe pas.
        """
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, f"Lieu '{place_id}' introuvable.")
        return place.to_dict(), 200

    @api.expect(place_model, validate=True)
    @api.marshal_with(place_response_model)
    def put(self, place_id):
        """
        PUT /api/v1/places/<place_id>
        Met à jour un lieu existant.

        Body attendu : un ou plusieurs champs à modifier.
        Réponse 200 : le lieu mis à jour.
        Réponse 404 : si l'id n'existe pas.
        Réponse 400 : si les données sont invalides.
        """
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, f"Lieu '{place_id}' introuvable.")

        try:
            updated = facade.update_place(place_id, api.payload)
        except ValueError as e:
            api.abort(400, str(e))

        return updated.to_dict(), 200


# ── /api/v1/places/<place_id>/reviews ─────────────────────────────────────────
@api.route("/<string:place_id>/reviews")
@api.param("place_id", "L'identifiant UUID du lieu")
class PlaceReviews(Resource):
    """Tous les avis d'un lieu."""

    def get(self, place_id):
        """
        GET /api/v1/places/<place_id>/reviews
        Retourne tous les avis associés à un lieu.
        Réponse 200 : liste des avis (vide si aucun).
        Réponse 404 : si le lieu n'existe pas.
        """
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, f"Lieu '{place_id}' introuvable.")

        reviews = facade.get_reviews_by_place(place_id)
        return [r.to_dict() for r in reviews], 200