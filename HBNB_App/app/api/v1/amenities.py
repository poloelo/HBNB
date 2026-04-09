"""
Amenity Endpoints — Task 4
==========================
Routes disponibles :
  POST   /api/v1/amenities/     → créer un amenity (JWT requis, admin seulement)
  GET    /api/v1/amenities/     → lister tous les amenities (public)
  GET    /api/v1/amenities/<id> → récupérer un amenity par id (public)
  PUT    /api/v1/amenities/<id> → mettre à jour un amenity (JWT requis, admin seulement)

DELETE n'est PAS implémenté dans cette partie.
"""

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt
from app.services import facade

# ── Namespace ─────────────────────────────────────────────────────────────────
api = Namespace("amenities", description="Opérations sur les amenities")

# ── Modèles Swagger ───────────────────────────────────────────────────────────
amenity_model = api.model(
    "Amenity",
    {
        "name": fields.String(
            required=True,
            description="Nom de l'amenity (ex: Wi-Fi, Piscine...)",
        ),
    },
)

amenity_response_model = api.model(
    "AmenityResponse",
    {
        "id":         fields.String(description="Identifiant unique UUID"),
        "name":       fields.String(description="Nom de l'amenity"),
        "created_at": fields.String(description="Date de création ISO 8601"),
        "updated_at": fields.String(description="Date de mise à jour ISO 8601"),
    },
)


# ── /api/v1/amenities/ ────────────────────────────────────────────────────────
@api.route("/")
class AmenityList(Resource):

    @api.marshal_list_with(amenity_response_model)
    def get(self):
        """GET /api/v1/amenities/ — Endpoint PUBLIC."""
        amenities = facade.get_all_amenities()
        return [a.to_dict() for a in amenities], 200

    @jwt_required()
    @api.expect(amenity_model, validate=True)
    @api.marshal_with(amenity_response_model, code=201)
    def post(self):
        """
        POST /api/v1/amenities/
        Crée un amenity. JWT requis, admin seulement.

        Réponse 201 : l'amenity créé.
        Réponse 400 : données invalides.
        Réponse 403 : l'utilisateur n'est pas administrateur.
        """
        claims = get_jwt()
        if not claims.get("is_admin", False):
            api.abort(403, "Seuls les administrateurs peuvent créer des amenities.")

        try:
            amenity = facade.create_amenity(api.payload)
        except ValueError as e:
            api.abort(400, str(e))

        return amenity.to_dict(), 201


# ── /api/v1/amenities/<amenity_id> ───────────────────────────────────────────
@api.route("/<string:amenity_id>")
@api.param("amenity_id", "L'identifiant unique UUID de l'amenity")
class AmenityResource(Resource):

    @api.marshal_with(amenity_response_model)
    def get(self, amenity_id):
        """GET /api/v1/amenities/<id> — Endpoint PUBLIC."""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, f"Amenity '{amenity_id}' introuvable.")
        return amenity.to_dict(), 200

    @jwt_required()
    @api.expect(amenity_model, validate=True)
    @api.marshal_with(amenity_response_model)
    def put(self, amenity_id):
        """
        PUT /api/v1/amenities/<id>
        Met à jour un amenity. JWT requis, admin seulement.

        Réponse 200 : l'amenity mis à jour.
        Réponse 400 : données invalides.
        Réponse 403 : l'utilisateur n'est pas administrateur.
        Réponse 404 : amenity introuvable.
        """
        claims = get_jwt()
        if not claims.get("is_admin", False):
            api.abort(403, "Seuls les administrateurs peuvent modifier des amenities.")

        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, f"Amenity '{amenity_id}' introuvable.")

        try:
            updated = facade.update_amenity(amenity_id, api.payload)
        except ValueError as e:
            api.abort(400, str(e))

        return updated.to_dict(), 200