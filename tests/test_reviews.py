"""
tests/test_reviews.py
---------------------
Integration tests for the Review model + Facade layer.
Run with:  python -m unittest tests.test_reviews -v   (from hbnb/)
"""

import unittest
from app.models.review import Review
from app.services.facade import HBnBFacade


class TestReviewModel(unittest.TestCase):

    def _make(self, **kw):
        defaults = dict(
            text="Great place",
            rating=5,
            user_id="user-uuid",
            place_id="place-uuid"
        )
        defaults.update(kw)
        return Review(**defaults)

    def test_to_dict_expected_keys(self):
        for key in (
            "id", "text", "rating",
            "user_id", "place_id",
            "created_at", "updated_at"
        ):
            self.assertIn(key, self._make().to_dict())

    def test_text_stripped(self):
        r = self._make(text="  Nice stay  ")
        self.assertEqual(r.text, "Nice stay")

    def test_empty_text_raises(self):
        with self.assertRaises(ValueError):
            self._make(text="")

    def test_rating_too_low_raises(self):
        with self.assertRaises(ValueError):
            self._make(rating=0)

    def test_rating_too_high_raises(self):
        with self.assertRaises(ValueError):
            self._make(rating=6)

    def test_update_text(self):
        r = self._make()
        r.update({"text": "Updated review"})
        self.assertEqual(r.text, "Updated review")

    def test_update_rating(self):
        r = self._make()
        r.update({"rating": 4})
        self.assertEqual(r.rating, 4)

    def test_update_refreshes_updated_at(self):
        r = self._make()
        before = r.updated_at
        r.update({"text": "Changed"})
        self.assertGreaterEqual(r.updated_at, before)

    def test_update_ignores_unknown_fields(self):
        r = self._make()
        r.update({"unknown": "value"})
        self.assertEqual(r.text, "Great place")


class TestHBnBFacadeReviews(unittest.TestCase):

    def setUp(self):
        self.facade = HBnBFacade()

        # create user
        self.user = self.facade.create_user({
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "password": "password123"
        })

        # create place
        self.place = self.facade.create_place({
            "name": "Test Place",
            "description": "Description",
            "city": "Dakar",
            "price_per_night": 50,
            "max_guests": 2,
            "owner_id": self.user.id
        })

    def _create(self, **kw):
        data = dict(
            text="Awesome",
            rating=5,
            user_id=self.user.id,
            place_id=self.place.id
        )
        data.update(kw)
        return self.facade.create_review(data)

    def test_create_review_returns_review(self):
        r = self._create()
        self.assertEqual(r.rating, 5)

    def test_create_review_persisted(self):
        r = self._create()
        self.assertEqual(self.facade.get_review(r.id).id, r.id)

    def test_create_review_invalid_user_raises(self):
        with self.assertRaises(ValueError):
            self._create(user_id="invalid-user")

    def test_create_review_invalid_place_raises(self):
        with self.assertRaises(ValueError):
            self._create(place_id="invalid-place")

    def test_get_review_existing(self):
        r = self._create()
        self.assertEqual(self.facade.get_review(r.id).id, r.id)

    def test_get_review_nonexistent_returns_none(self):
        self.assertIsNone(self.facade.get_review("bad-id"))

    def test_get_all_reviews_empty(self):
        self.assertEqual(self.facade.get_all_reviews(), [])

    def test_get_all_reviews_multiple(self):
        self._create()
        self._create(text="Good")
        self._create(text="Okay")
        self.assertEqual(len(self.facade.get_all_reviews()), 3)

    def test_update_review_text(self):
        r = self._create()
        updated = self.facade.update_review(r.id, {"text": "Updated"})
        self.assertEqual(updated.text, "Updated")

    def test_update_review_rating(self):
        r = self._create()
        updated = self.facade.update_review(r.id, {"rating": 3})
        self.assertEqual(updated.rating, 3)

    def test_update_review_nonexistent_returns_none(self):
        self.assertIsNone(
            self.facade.update_review("bad-id", {"text": "X"})
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
