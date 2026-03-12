"""
Auth Endpoints — Task 2
=======================
Routes disponibles :
  POST /api/v1/auth/login  → authentifier un utilisateur et retourner un JWT
"""

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app.services import facade

# ── Namespace ──────────────────────────────────────────────────────────────────
api = Namespace("auth", description="Authentification JWT")

# ── Modèle d'entrée ────────────────────────────────────────────────────────────
login_model = api.model(
    "Login",
    {
        "email":    fields.String(required=True, description="Adresse email"),
        "password": fields.String(required=True, description="Mot de passe en clair"),
    },
)


# ── POST /api/v1/auth/login ────────────────────────────────────────────────────
@api.route("/login")
class Login(Resource):

    @api.expect(login_model, validate=True)
    def post(self):
        """
        POST /api/v1/auth/login
        Vérifie les identifiants et retourne un JWT signé.

        Claims embarqués dans le token :
          - sub      : user.id  (identifiant du sujet)
          - is_admin : user.is_admin  (pour l'autorisation future)

        Réponse 200 : { "access_token": "<jwt>" }
        Réponse 401 : identifiants invalides
        """
        credentials = api.payload

        # 1. Récupérer l'utilisateur par email
        user = facade.get_user_by_email(credentials["email"])
        if not user:
            api.abort(401, "Email ou mot de passe incorrect.")

        # 2. Vérifier le mot de passe avec bcrypt
        if not user.verify_password(credentials["password"]):
            api.abort(401, "Email ou mot de passe incorrect.")

        # 3. Créer le token JWT avec les claims additionnels
        #    additional_claims permet d'embarquer is_admin dans le payload du token
        access_token = create_access_token(
            identity=user.id,
            additional_claims={"is_admin": user.is_admin}
        )

        return {"access_token": access_token}, 200
