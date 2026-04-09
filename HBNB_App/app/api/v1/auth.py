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
        credentials = api.payload
        print("DEBUG credentials reçus:", credentials)

        # 1. Récupérer l'utilisateur par email
        user = facade.get_user_by_email(credentials["email"])
        print("DEBUG user trouvé:", user)

        if not user:
            api.abort(401, "Email ou mot de passe incorrect.")

        # 2. Vérifier le mot de passe avec bcrypt
        pwd_ok = user.verify_password(credentials["password"])
        print("DEBUG password ok:", pwd_ok)

        if not pwd_ok:
            api.abort(401, "Email ou mot de passe incorrect.")

        # 3. Créer le token JWT
        access_token = create_access_token(
            identity=user.id,
            additional_claims={"is_admin": user.is_admin}
        )
        return {"access_token": access_token}, 200