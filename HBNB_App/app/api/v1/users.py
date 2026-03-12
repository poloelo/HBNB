"""
User Endpoints — Task 2
=======================
Routes disponibles :
  POST   /api/v1/users/       → créer un utilisateur
  GET    /api/v1/users/       → lister tous les utilisateurs
  GET    /api/v1/users/<id>   → récupérer un utilisateur par id
  PUT    /api/v1/users/<id>   → mettre à jour un utilisateur

DELETE n'est PAS implémenté dans cette partie.
"""

from flask_restx import Namespace, Resource, fields
from app.services import facade

# ── Namespace ──────────────────────────────────────────────────────────────────
api = Namespace("users", description="Opérations sur les utilisateurs")

# ── Modèle d'entrée (validation + Swagger) ─────────────────────────────────────
user_model = api.model(
    "User",
    {
        "first_name": fields.String(required=True,  description="Prénom (max 50 car.)"),
        "last_name":  fields.String(required=True,  description="Nom (max 50 car.)"),
        "email":      fields.String(required=True,  description="Adresse email valide et unique"),
        "is_admin":   fields.Boolean(required=False, default=False, description="Rôle admin"),
    },
)

# ── Modèle de réponse (filtre les champs exposés) ──────────────────────────────
user_response_model = api.model(
    "UserResponse",
    {
        "id":         fields.String(description="UUID unique"),
        "first_name": fields.String(description="Prénom"),
        "last_name":  fields.String(description="Nom"),
        "email":      fields.String(description="Email"),
        "is_admin":   fields.Boolean(description="Admin ?"),
        "created_at": fields.String(description="Date de création ISO 8601"),
        "updated_at": fields.String(description="Date de mise à jour ISO 8601"),
    },
)


# ── /api/v1/users/ ─────────────────────────────────────────────────────────────
@api.route("/")
class UserList(Resource):
    """Collection d'utilisateurs."""

    @api.marshal_list_with(user_response_model)
    def get(self):
        """
        GET /api/v1/users/
        Retourne la liste de tous les utilisateurs.
        Réponse 200 : liste JSON.
        """
        users = facade.get_all_users()
        return [u.to_dict() for u in users], 200

    @api.expect(user_model, validate=True)
    @api.marshal_with(user_response_model, code=201)
    def post(self):
        """
        POST /api/v1/users/
        Crée un nouvel utilisateur.

        Body attendu : { "first_name": "Alice", "last_name": "Martin", "email": "alice@example.com" }
        Réponse 201 : l'utilisateur créé.
        Réponse 400 : champ invalide ou email déjà utilisé.
        """
        try:
            user = facade.create_user(api.payload)
        except ValueError as e:
            api.abort(400, str(e))

        return user.to_dict(), 201


# ── /api/v1/users/<user_id> ────────────────────────────────────────────────────
@api.route("/<string:user_id>")
@api.param("user_id", "L'identifiant UUID de l'utilisateur")
class UserResource(Resource):
    """Ressource individuelle d'un utilisateur."""

    @api.marshal_with(user_response_model)
    def get(self, user_id):
        """
        GET /api/v1/users/<user_id>
        Retourne un utilisateur par son id.
        Réponse 200 : l'utilisateur trouvé.
        Réponse 404 : si l'id n'existe pas.
        """
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, f"Utilisateur '{user_id}' introuvable.")
        return user.to_dict(), 200

    @api.expect(user_model, validate=True)
    @api.marshal_with(user_response_model)
    def put(self, user_id):
        """
        PUT /api/v1/users/<user_id>
        Met à jour un utilisateur existant.

        Body attendu : un ou plusieurs champs à modifier.
        Réponse 200 : l'utilisateur mis à jour.
        Réponse 404 : si l'id n'existe pas.
        Réponse 400 : si les données sont invalides (email dupliqué, format incorrect...).
        """
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, f"Utilisateur '{user_id}' introuvable.")

        try:
            updated = facade.update_user(user_id, api.payload)
        except ValueError as e:
            api.abort(400, str(e))

        return updated.to_dict(), 200
