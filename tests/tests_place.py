
"""
tests/test_places.py
--------------------
Integration tests for the Place model + Facade layer.
Run with:  python -m unittest tests.test_places -v   (from hbnb/)
"""

import unittest
from app.models.place import Place
from app.services.facade import HBnBFacade


class TestPlaceModel(unittest.TestCase):

    def _make(self, **kw):
        defaults = dict(
            name="Nice place",
            description="A very nice place",
            city="Paris",
            price_per_night=100,
            max_guests=2,
            owner_id="owner-uuid"
        )
        defaults.update(kw)
        return Place(**defaults)

    def test_to_dict_expected_keys(self):
        for key in (
            "id", "name", "description", "city",
            "price_per_night", "max_guests",
            "owner_id", "created_at", "updated_at"
        ):
            self.assertIn(key, self._make().to_dict())

    def test_name_stripped(self):
        p = self._make(name="  House  ")
        self.assertEqual(p.name, "House")

    def test_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self._make(name="")

    def test_name_too_long_raises(self):
        with self.assertRaises(ValueError):
            self._make(name="A" * 101)

    def test_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self._make(price_per_night=-10)

    def test_zero_price_raises(self):
        with self.assertRaises(ValueError):
            self._make(price_per_night=0)

    def test_invalid_max_guests_raises(self):
        with self.assertRaises(ValueError):
            self._make(max_guests=0)

    def test_update_name(self):
        p = self._make()
        p.update({"name": "Updated"})
        self.assertEqual(p.name, "Updated")

    def test_update_price(self):
        p = self._make()
        p.update({"price_per_night": 150})
        self.assertEqual(p.price_per_night, 150)

    def test_update_refreshes_updated_at(self):
        p = self._make()
        before = p.updated_at
        p.update({"name": "Changed"})
        self.assertGreaterEqual(p.updated_at, before)

    def test_update_ignores_unknown_fields(self):
        p = self._make()
        p.update({"unknown": "value"})
        self.assertEqual(p.name, "Nice place")


class TestHBnBFacadePlaces(unittest.TestCase):

    def setUp(self):
        self.facade = HBnBFacade()

        # create owner user
        self.owner = self.facade.create_user({
            "first_name": "Owner",
            "last_name": "User",
            "email": "owner@example.com",
            "password": "password123"
        })

    def _create(self, **kw):
        data = dict(
            name="My Place",
            description="Description",
            city="Dakar",
            price_per_night=80,
            max_guests=4,
            owner_id=self.owner.id
        )
        data.update(kw)
        return self.facade.create_place(data)

    def test_create_place_returns_place(self):
        p = self._create()
        self.assertEqual(p.name, "My Place")

    def test_create_place_persisted(self):
        p = self._create()
        self.assertEqual(self.facade.get_place(p.id).id, p.id)

    def test_create_place_invalid_owner_raises(self):
        with self.assertRaises(ValueError):
            self._create(owner_id="invalid-owner")

    def test_get_place_existing(self):
        p = self._create()
        self.assertEqual(self.facade.get_place(p.id).id, p.id)

    def test_get_place_nonexistent_returns_none(self):
        self.assertIsNone(self.facade.get_place("bad-id"))

    def test_get_all_places_empty(self):
        self.assertEqual(self.facade.get_all_places(), [])

    def test_get_all_places_multiple(self):
        self._create(name="A")
        self._create(name="B")
        self._create(name="C")
        self.assertEqual(len(self.facade.get_all_places()), 3)

    def test_update_place_name(self):
        p = self._create()
        updated = self.facade.update_place(p.id, {"name": "Updated"})
        self.assertEqual(updated.name, "Updated")

    def test_update_place_price(self):
        p = self._create()
        updated = self.facade.update_place(p.id, {"price_per_night": 120})
        self.assertEqual(updated.price_per_night, 120)

    def test_update_place_nonexistent_returns_none(self):
        self.assertIsNone(
            self.facade.update_place("bad-id", {"name": "X"})
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

