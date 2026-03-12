## `app/api/v1/reviews.py` — **Endpoints uniquement**


"""
app/api/v1/reviews.py
---------------------
Presentation layer  Review endpoints.
"""

from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace("reviews", description="Review operations")

# Swagger models
review_create_model = api.model("ReviewCreate", {
    "user_id": fields.String(required=True),
    "place_id": fields.String(required=True),
    "text": fields.String(required=True),
    "rating": fields.Integer(required=True, min=1, max=5),
})

review_update_model = api.model("ReviewUpdate", {
    "text": fields.String(),
    "rating": fields.Integer(min=1, max=5),
})

review_response_model = api.model("ReviewResponse", {
    "id": fields.String(),
    "user_id": fields.String(),
    "place_id": fields.String(),
    "text": fields.String(),
    "rating": fields.Integer(),
    "created_at": fields.String(),
    "updated_at": fields.String(),
})


@api.route("/")
class ReviewList(Resource):

    @api.expect(review_create_model, validate=True)
    @api.marshal_with(review_response_model, code=201)
    def post(self):
        review = facade.create_review(api.payload)
        return review.to_dict(), 201

    @api.marshal_list_with(review_response_model)
    def get(self):
        return [r.to_dict() for r in facade.get_all_reviews()], 200


@api.route("/<string:review_id>")
@api.param("review_id", "Review UUID")
class ReviewDetail(Resource):

    @api.marshal_with(review_response_model)
    def get(self, review_id):
        review = facade.get_review(review_id)
        if review is None:
            api.abort(404, "Review not found.")
        return review.to_dict(), 200

    @api.expect(review_update_model, validate=True)
    @api.marshal_with(review_response_model)
    def put(self, review_id):
        data = api.payload
        if not data:
            api.abort(400, "No updatable fields provided.")

        review = facade.update_review(review_id, data)
        if review is None:
            api.abort(404, "Review not found.")

        return review.to_dict(), 200
