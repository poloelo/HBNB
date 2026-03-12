"""
User Endpoints — Task 3
=======================
Routes disponibles :
  POST   /api/v1/users/       → créer un utilisateur (public)
  GET    /api/v1/users/       → lister tous les utilisateurs (public)
  GET    /api/v1/users/<id>   → récupérer un utilisateur par id (public)
  PUT    /api/v1/users/<id>   → mettre à jour son propre profil (JWT requis)
                                 email et password NON modifiables via cet endpoint

DELETE n'est PAS implémenté dans cette partie.
"""

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import facade

# ── Namespace ──────────────────────────────────────────────────────────────────
api = Namespace("users", description="Opérations sur les utilisateurs")

# ── Modèle d'entrée pour la création (POST) ────────────────────────────────────
user_model = api.model(
    "User",
    {
        "first_name": fields.String(required=True,  description="Prénom (max 50 car.)"),
        "last_name":  fields.String(required=True,  description="Nom (max 50 car.)"),
        "email":      fields.String(required=True,  description="Adresse email valide et unique"),
        "password":   fields.String(required=True,  description="Mot de passe (sera haché, non retourné)"),
        "is_admin":   fields.Boolean(required=False, default=False, description="Rôle admin"),
    },
)

# ── Modèle d'entrée pour la mise à jour (PUT) ──────────────────────────────────
# Email et password exclus : ne peuvent pas être modifiés via cet endpoint.
user_update_model = api.model(
    "UserUpdate",
    {
        "first_name": fields.String(required=False, description="Prénom (max 50 car.)"),
        "last_name":  fields.String(required=False, description="Nom (max 50 car.)"),
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
        Endpoint PUBLIC — aucun token requis.
        Retourne la liste de tous les utilisateurs.
        """
        users = facade.get_all_users()
        return [u.to_dict() for u in users], 200

    @api.expect(user_model, validate=True)
    @api.marshal_with(user_response_model, code=201)
    def post(self):
        """
        POST /api/v1/users/
        Endpoint PUBLIC — inscription d'un nouvel utilisateur.

        Body attendu : { "first_name": ..., "last_name": ..., "email": ..., "password": ... }
        Réponse 201 : l'utilisateur créé (sans le password).
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
        Endpoint PUBLIC — aucun token requis.
        Retourne un utilisateur par son id.
        """
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, f"Utilisateur '{user_id}' introuvable.")
        return user.to_dict(), 200

    @jwt_required()
    @api.expect(user_update_model, validate=True)
    @api.marshal_with(user_response_model)
    def put(self, user_id):
        """
        PUT /api/v1/users/<user_id>
        Met à jour son propre profil. JWT requis.

        Règles :
          - L'utilisateur connecté ne peut modifier QUE son propre profil (403 sinon).
          - Email et password ne sont PAS modifiables via cet endpoint (400 si présents).
          - Seuls first_name et last_name sont acceptés.

        Réponse 200 : l'utilisateur mis à jour.
        Réponse 400 : tentative de modification email/password ou données invalides.
        Réponse 403 : tentative de modifier le profil d'un autre utilisateur.
        Réponse 404 : utilisateur introuvable.
        """
        current_user_id = get_jwt_identity()

        # Contrôle d'ownership : un user ne peut modifier que son propre profil
        if current_user_id != user_id:
            api.abort(403, "Vous ne pouvez modifier que votre propre profil.")

        user = facade.get_user(user_id)
        if not user:
            api.abort(404, f"Utilisateur '{user_id}' introuvable.")

        # Email et password ne sont pas modifiables via cet endpoint
        data = api.payload
        if "email" in data or "password" in data:
            api.abort(400, "Modification de l'email ou du mot de passe non autorisée ici.")

        try:
            updated = facade.update_user(user_id, data)
        except ValueError as e:
            api.abort(400, str(e))

        return updated.to_dict(), 200
