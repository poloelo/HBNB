"""
User Endpoints — Task 4
=======================
Routes disponibles :
  POST   /api/v1/users/       → créer un utilisateur
                                 Public : is_admin forcé à False
                                 Admin  : peut définir is_admin librement
  GET    /api/v1/users/       → lister tous les utilisateurs (public)
  GET    /api/v1/users/<id>   → récupérer un utilisateur par id (public)
  PUT    /api/v1/users/<id>   → mettre à jour un profil (JWT requis)
                                 User normal : son propre profil, first_name/last_name seul.
                                 Admin       : n'importe quel profil + email + password.

DELETE n'est PAS implémenté dans cette partie.
"""

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
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
        "is_admin":   fields.Boolean(required=False, default=False, description="Rôle admin (admin seulement)"),
    },
)

# ── Modèle d'entrée pour la mise à jour (PUT) ──────────────────────────────────
# Tous les champs sont optionnels.
# Les règles d'accès sont enforced dans le handler, pas dans le modèle :
#   - User normal : seuls first_name / last_name acceptés
#   - Admin       : email et password aussi modifiables
user_update_model = api.model(
    "UserUpdate",
    {
        "first_name": fields.String(required=False, description="Prénom (max 50 car.)"),
        "last_name":  fields.String(required=False, description="Nom (max 50 car.)"),
        "email":      fields.String(required=False, description="(Admin uniquement) Nouvel email"),
        "password":   fields.String(required=False, description="(Admin uniquement) Nouveau mot de passe"),
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
        """GET /api/v1/users/ — Endpoint PUBLIC."""
        users = facade.get_all_users()
        return [u.to_dict() for u in users], 200

    @api.expect(user_model, validate=True)
    @api.marshal_with(user_response_model, code=201)
    def post(self):
        """
        POST /api/v1/users/
        Crée un utilisateur.

        - Sans JWT (public) : is_admin est ignoré et forcé à False.
        - Avec JWT admin : is_admin est pris en compte tel quel.
        """
        data = dict(api.payload)

        # Seul un admin peut créer un utilisateur avec is_admin=True
        # Sans token valide, is_admin est ignoré (forcé False)
        try:
            claims = get_jwt()
            caller_is_admin = claims.get("is_admin", False)
        except Exception:
            caller_is_admin = False

        if not caller_is_admin:
            data["is_admin"] = False

        try:
            user = facade.create_user(data)
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
        """GET /api/v1/users/<user_id> — Endpoint PUBLIC."""
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
        Met à jour un profil utilisateur. JWT requis.

        User normal :
          - Ne peut modifier QUE son propre profil (403 sinon).
          - Seuls first_name et last_name sont acceptés (400 si email/password présents).

        Admin :
          - Peut modifier n'importe quel profil.
          - Peut modifier email (unicité vérifiée) et password (rehaché).
        """
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get("is_admin", False)

        # Vérification d'ownership pour les non-admins
        if not is_admin and current_user_id != user_id:
            api.abort(403, "Vous ne pouvez modifier que votre propre profil.")

        user = facade.get_user(user_id)
        if not user:
            api.abort(404, f"Utilisateur '{user_id}' introuvable.")

        data = dict(api.payload)

        # Un user normal ne peut pas modifier email ni password
        if not is_admin:
            if "email" in data or "password" in data:
                api.abort(400, "Modification de l'email ou du mot de passe non autorisée.")

        try:
            updated = facade.update_user(user_id, data)
        except ValueError as e:
            api.abort(400, str(e))

        return updated.to_dict(), 200
