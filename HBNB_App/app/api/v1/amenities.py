"""
Amenity Endpoints — Task 3
==========================
Routes disponibles :
  POST   /api/v1/amenities/          → créer un amenity
  GET    /api/v1/amenities/          → lister tous les amenities
  GET    /api/v1/amenities/<id>      → récupérer un amenity par id
  PUT    /api/v1/amenities/<id>      → mettre à jour un amenity

DELETE n'est PAS implémenté dans cette partie.
"""

from flask_restx import Namespace, Resource, fields
from app.services import facade

# ── Namespace ─────────────────────────────────────────────────────────────────
# Un Namespace regroupe les routes liées à une même ressource.
# Le préfixe /api/v1/amenities est déclaré dans create_app().
api = Namespace("amenities", description="Opérations sur les amenities")

# ── Modèle de sérialisation (swagger + validation entrée) ─────────────────────
# flask-restx utilise ce modèle pour :
#   1. Générer automatiquement la doc Swagger
#   2. Valider les champs requis dans le body JSON des requêtes
amenity_model = api.model(
    "Amenity",
    {
        "name": fields.String(
            required=True,
            description="Nom de l'amenity (ex: Wi-Fi, Piscine...)",
        ),
    },
)

# Modèle de réponse : inclut les champs générés (id, timestamps)
amenity_response_model = api.model(
    "AmenityResponse",
    {
        "id": fields.String(description="Identifiant unique UUID"),
        "name": fields.String(description="Nom de l'amenity"),
        "created_at": fields.String(description="Date de création ISO 8601"),
        "updated_at": fields.String(description="Date de mise à jour ISO 8601"),
    },
)


# ── /api/v1/amenities/ ────────────────────────────────────────────────────────
@api.route("/")
class AmenityList(Resource):
    """
    Collection d'amenities.
    Regroupe les opérations sur la liste complète.
    """

    @api.marshal_list_with(amenity_response_model)
    def get(self):
        """
        GET /api/v1/amenities/
        Retourne la liste de tous les amenities.
        Réponse 200 : liste JSON des amenities.
        """
        amenities = facade.get_all_amenities()
        # marshal_list_with sérialise automatiquement la liste
        return [a.to_dict() for a in amenities], 200

    @api.expect(amenity_model, validate=True)
    @api.marshal_with(amenity_response_model, code=201)
    def post(self):
        """
        POST /api/v1/amenities/
        Crée un nouvel amenity.

        Body attendu : { "name": "Wi-Fi" }
        Réponse 201 : l'amenity créé.
        Réponse 400 : si le nom est manquant ou invalide.
        """
        data = api.payload  # dict parsé depuis le body JSON

        try:
            amenity = facade.create_amenity(data)
        except ValueError as e:
            # 400 Bad Request pour toute erreur de validation métier
            api.abort(400, str(e))

        return amenity.to_dict(), 201


# ── /api/v1/amenities/<amenity_id> ───────────────────────────────────────────
@api.route("/<string:amenity_id>")
@api.param("amenity_id", "L'identifiant unique UUID de l'amenity")
class AmenityResource(Resource):
    """
    Ressource individuelle d'un amenity.
    Regroupe les opérations sur un seul amenity identifié par son UUID.
    """

    @api.marshal_with(amenity_response_model)
    def get(self, amenity_id):
        """
        GET /api/v1/amenities/<amenity_id>
        Retourne un amenity par son id.
        Réponse 200 : l'amenity trouvé.
        Réponse 404 : si l'id n'existe pas.
        """
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, f"Amenity '{amenity_id}' introuvable.")
        return amenity.to_dict(), 200

    @api.expect(amenity_model, validate=True)
    @api.marshal_with(amenity_response_model)
    def put(self, amenity_id):
        """
        PUT /api/v1/amenities/<amenity_id>
        Met à jour un amenity existant.

        Body attendu : { "name": "Nouveau nom" }
        Réponse 200 : l'amenity mis à jour.
        Réponse 404 : si l'id n'existe pas.
        Réponse 400 : si les données sont invalides.
        """
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, f"Amenity '{amenity_id}' introuvable.")

        try:
            updated = facade.update_amenity(amenity_id, api.payload)
        except ValueError as e:
            api.abort(400, str(e))

        return updated.to_dict(), 200
