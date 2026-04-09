"""
tests/test_amenities.py
-----------------------
Integration tests for the Amenity model + Facade layer.
Run with:  python -m unittest tests.test_amenities -v   (from hbnb/)
"""

import unittest
from app.models.amenity import Amenity
from app.services.facade import HBnBFacade


class TestAmenityModel(unittest.TestCase):

    def _make(self, **kw):
        defaults = dict(
            name="Wi-Fi"
        )
        defaults.update(kw)
        return Amenity(**defaults)

    def test_to_dict_expected_keys(self):
        for key in ("id", "name", "created_at", "updated_at"):
            self.assertIn(key, self._make().to_dict())

    def test_name_stripped(self):
        a = self._make(name="  Pool  ")
        self.assertEqual(a.name, "Pool")

    def test_empty_name_raises(self):
        with self.assertRaises(ValueError):
            self._make(name="")

    def test_name_too_long_raises(self):
        with self.assertRaises(ValueError):
            self._make(name="A" * 51)

    def test_update_name(self):
        a = self._make()
        a.update({"name": "Parking"})
        self.assertEqual(a.name, "Parking")

    def test_update_refreshes_updated_at(self):
        a = self._make()
        before = a.updated_at
        a.update({"name": "Changed"})
        self.assertGreaterEqual(a.updated_at, before)

    def test_update_ignores_unknown_fields(self):
        a = self._make()
        a.update({"unknown": "value"})
        self.assertEqual(a.name, "Wi-Fi")


class TestHBnBFacadeAmenities(unittest.TestCase):

    def setUp(self):
        self.facade = HBnBFacade()

    def _create(self, name="Wi-Fi"):
        return self.facade.create_amenity({"name": name})

    def test_create_amenity_returns_amenity(self):
        a = self._create()
        self.assertEqual(a.name, "Wi-Fi")

    def test_create_amenity_persisted(self):
        a = self._create()
        self.assertEqual(self.facade.get_amenity(a.id).id, a.id)

    def test_create_duplicate_amenity_raises(self):
        self._create("Pool")
        with self.assertRaises(ValueError):
            self._create("Pool")

    def test_get_amenity_existing(self):
        a = self._create()
        self.assertEqual(self.facade.get_amenity(a.id).id, a.id)

    def test_get_amenity_nonexistent_returns_none(self):
        self.assertIsNone(self.facade.get_amenity("bad-id"))

    def test_get_all_amenities_empty(self):
        self.assertEqual(self.facade.get_all_amenities(), [])

    def test_get_all_amenities_multiple(self):
        self._create("Wi-Fi")
        self._create("Parking")
        self._create("Pool")
        self.assertEqual(len(self.facade.get_all_amenities()), 3)

    def test_update_amenity_name(self):
        a = self._create("Old")
        updated = self.facade.update_amenity(a.id, {"name": "New"})
        self.assertEqual(updated.name, "New")

    def test_update_amenity_nonexistent_returns_none(self):
        self.assertIsNone(
            self.facade.update_amenity("bad-id", {"name": "X"})
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
