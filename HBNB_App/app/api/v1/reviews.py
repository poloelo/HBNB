"""
Review Endpoints — Task 3
=========================
Routes disponibles :
  POST   /api/v1/reviews/          → créer un avis (JWT requis)
  GET    /api/v1/reviews/          → lister tous les avis (public)
  GET    /api/v1/reviews/<id>      → récupérer un avis (public)
  PUT    /api/v1/reviews/<id>      → modifier son avis (JWT requis, auteur seulement)
  DELETE /api/v1/reviews/<id>      → supprimer son avis (JWT requis, auteur seulement)

Règles métier :
  - Un utilisateur ne peut pas laisser un avis sur son propre lieu.
  - Un utilisateur ne peut pas laisser deux avis pour le même lieu.
  - Seul l'auteur d'un avis peut le modifier ou le supprimer.
"""

from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace("reviews", description="Review operations")

# ── Swagger models ─────────────────────────────────────────────────────────────
review_create_model = api.model("ReviewCreate", {
    "place_id": fields.String(required=True,  description="UUID du lieu à évaluer"),
    "text":     fields.String(required=True,  description="Contenu de l'avis"),
    "rating":   fields.Integer(required=True, min=1, max=5, description="Note de 1 à 5"),
})

review_update_model = api.model("ReviewUpdate", {
    "text":   fields.String(description="Nouveau contenu de l'avis"),
    "rating": fields.Integer(min=1, max=5, description="Nouvelle note de 1 à 5"),
})

review_response_model = api.model("ReviewResponse", {
    "id":         fields.String(),
    "user_id":    fields.String(),
    "place_id":   fields.String(),
    "text":       fields.String(),
    "rating":     fields.Integer(),
    "created_at": fields.String(),
    "updated_at": fields.String(),
})


# ── /api/v1/reviews/ ──────────────────────────────────────────────────────────
@api.route("/")
class ReviewList(Resource):

    @jwt_required()
    @api.expect(review_create_model, validate=True)
    @api.marshal_with(review_response_model, code=201)
    def post(self):
        """
        POST /api/v1/reviews/
        Crée un avis. JWT requis.

        L'auteur est identifié par le JWT (user_id non accepté dans le body).

        Règles :
          - L'auteur ne peut pas être le propriétaire du lieu → 403.
          - L'auteur ne peut pas avoir déjà évalué ce lieu → 400.
        """
        current_user_id = get_jwt_identity()
        data = api.payload

        # Vérifier que le lieu existe
        place = facade.get_place(data["place_id"])
        if not place:
            api.abort(404, f"Lieu '{data['place_id']}' introuvable.")

        # Règle 1 : l'auteur ne peut pas évaluer son propre lieu
        if place.owner.id == current_user_id:
            api.abort(403, "Vous ne pouvez pas laisser un avis sur votre propre lieu.")

        # Règle 2 : pas de review en double pour le même lieu
        if facade.get_review_by_user_and_place(current_user_id, data["place_id"]):
            api.abort(400, "Vous avez déjà laissé un avis pour ce lieu.")

        # Le user_id vient du JWT, pas du payload
        data["user_id"] = current_user_id

        try:
            review = facade.create_review(data)
        except ValueError as e:
            api.abort(400, str(e))

        return review.to_dict(), 201

    @api.marshal_list_with(review_response_model)
    def get(self):
        """GET /api/v1/reviews/ — Endpoint PUBLIC."""
        return [r.to_dict() for r in facade.get_all_reviews()], 200


# ── /api/v1/reviews/<review_id> ───────────────────────────────────────────────
@api.route("/<string:review_id>")
@api.param("review_id", "Review UUID")
class ReviewDetail(Resource):

    @api.marshal_with(review_response_model)
    def get(self, review_id):
        """GET /api/v1/reviews/<id> — Endpoint PUBLIC."""
        review = facade.get_review(review_id)
        if review is None:
            api.abort(404, "Avis introuvable.")
        return review.to_dict(), 200

    @jwt_required()
    @api.expect(review_update_model, validate=True)
    @api.marshal_with(review_response_model)
    def put(self, review_id):
        """
        PUT /api/v1/reviews/<id>
        Modifie un avis. JWT requis.

        Règle : seul l'auteur de l'avis peut le modifier → 403 sinon.
        """
        current_user_id = get_jwt_identity()
        is_admin = get_jwt().get("is_admin", False)

        review = facade.get_review(review_id)
        if review is None:

            api.abort(404, "Avis introuvable.")

        # Contrôle d'ownership : auteur ou admin
        if not is_admin and review.user.id != current_user_id:
            api.abort(403, "Vous ne pouvez modifier que vos propres avis.")

        data = api.payload
        if not data:
            api.abort(400, "Aucun champ à mettre à jour.")

        updated = facade.update_review(review_id, data)
        return updated.to_dict(), 200

    @jwt_required()
    def delete(self, review_id):
        """
        DELETE /api/v1/reviews/<id>
        Supprime un avis. JWT requis.

        Règle : seul l'auteur de l'avis peut le supprimer → 403 sinon.
        Réponse 200 : confirmation de suppression.
        """
        current_user_id = get_jwt_identity()
        is_admin = get_jwt().get("is_admin", False)

        review = facade.get_review(review_id)
        if review is None:
            api.abort(404, "Avis introuvable.")

        # Contrôle d'ownership : auteur ou admin
        if not is_admin and review.user.id != current_user_id:
            api.abort(403, "Vous ne pouvez supprimer que vos propres avis.")

        facade.delete_review(review_id)
        return {"message": "Avis supprimé avec succès."}, 200