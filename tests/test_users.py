"""
tests/test_users.py
-------------------
Integration tests for the User model + Facade layer.
Run with:  python -m unittest tests.test_users -v   (from hbnb/)
"""

import unittest
from app.models.user import User
from app.services.facade import HBnBFacade


class TestUserModel(unittest.TestCase):

    def _make(self, **kw):
        defaults = dict(
            first_name="Jane", last_name="Doe",
            email="jane@example.com", password="secret123"
        )
        defaults.update(kw)
        return User(**defaults)

    def test_to_dict_excludes_password(self):
        self.assertNotIn("password", self._make().to_dict())

    def test_to_dict_includes_expected_keys(self):
        for key in ("id", "first_name", "last_name", "email",
                    "is_admin", "created_at", "updated_at"):
            self.assertIn(key, self._make().to_dict())

    def test_email_stored_lowercase(self):
        self.assertEqual(self._make(email="UPPER@EXAMPLE.COM").email,
                         "upper@example.com")

    def test_names_stripped(self):
        u = self._make(first_name="  Alice  ", last_name="  Smith  ")
        self.assertEqual(u.first_name, "Alice")
        self.assertEqual(u.last_name, "Smith")

    def test_is_admin_defaults_false(self):
        self.assertFalse(self._make().is_admin)

    def test_is_admin_set_true(self):
        self.assertTrue(self._make(is_admin=True).is_admin)

    def test_invalid_email_raises(self):
        with self.assertRaises(ValueError):
            self._make(email="not-an-email")

    def test_empty_first_name_raises(self):
        with self.assertRaises(ValueError):
            self._make(first_name="")

    def test_first_name_too_long_raises(self):
        with self.assertRaises(ValueError):
            self._make(first_name="A" * 51)

    def test_short_password_raises(self):
        with self.assertRaises(ValueError):
            self._make(password="abc")

    def test_empty_password_raises(self):
        with self.assertRaises(ValueError):
            self._make(password="")

    def test_update_first_name(self):
        u = self._make()
        u.update({"first_name": "Updated"})
        self.assertEqual(u.first_name, "Updated")

    def test_update_email(self):
        u = self._make()
        u.update({"email": "new@example.com"})
        self.assertEqual(u.email, "new@example.com")

    def test_update_email_lowercased(self):
        u = self._make()
        u.update({"email": "NEW@EXAMPLE.COM"})
        self.assertEqual(u.email, "new@example.com")

    def test_update_bad_email_raises(self):
        u = self._make()
        with self.assertRaises(ValueError):
            u.update({"email": "bad"})

    def test_update_refreshes_updated_at(self):
        u = self._make()
        before = u.updated_at
        u.update({"first_name": "Changed"})
        self.assertGreaterEqual(u.updated_at, before)

    def test_update_ignores_unknown_keys(self):
        u = self._make()
        u.update({"nonsense_field": "value"})
        self.assertEqual(u.first_name, "Jane")


class TestHBnBFacadeUsers(unittest.TestCase):

    def setUp(self):
        self.facade = HBnBFacade()

    def _create(self, email="alice@example.com", **kw):
        data = dict(first_name="Alice", last_name="Smith",
                    email=email, password="password1")
        data.update(kw)
        return self.facade.create_user(data)

    def test_create_user_returns_user(self):
        u = self._create()
        self.assertEqual(u.email, "alice@example.com")

    def test_create_user_persisted(self):
        u = self._create()
        self.assertEqual(self.facade.get_user(u.id).id, u.id)

    def test_create_user_duplicate_email_raises(self):
        self._create()
        with self.assertRaises(ValueError):
            self._create()

    def test_create_user_invalid_email_raises(self):
        with self.assertRaises(ValueError):
            self._create(email="not-valid")

    def test_get_user_existing(self):
        u = self._create()
        self.assertEqual(self.facade.get_user(u.id).id, u.id)

    def test_get_user_nonexistent_returns_none(self):
        self.assertIsNone(self.facade.get_user("does-not-exist"))

    def test_get_user_by_email(self):
        self._create(email="find@me.com")
        self.assertIsNotNone(self.facade.get_user_by_email("find@me.com"))

    def test_get_user_by_email_case_insensitive(self):
        self._create(email="Mixed@Case.com")
        self.assertIsNotNone(self.facade.get_user_by_email("MIXED@CASE.COM"))

    def test_get_user_by_email_not_found(self):
        self.assertIsNone(self.facade.get_user_by_email("ghost@nowhere.com"))

    def test_get_all_users_empty(self):
        self.assertEqual(self.facade.get_all_users(), [])

    def test_get_all_users_multiple(self):
        self._create("a@a.com")
        self._create("b@b.com")
        self._create("c@c.com")
        self.assertEqual(len(self.facade.get_all_users()), 3)

    def test_update_user_first_name(self):
        u = self._create()
        updated = self.facade.update_user(u.id, {"first_name": "Bob"})
        self.assertEqual(updated.first_name, "Bob")

    def test_update_user_email(self):
        u = self._create()
        updated = self.facade.update_user(u.id, {"email": "new@email.com"})
        self.assertEqual(updated.email, "new@email.com")

    def test_update_user_email_conflict_raises(self):
        u1 = self._create("u1@x.com")
        u2 = self._create("u2@x.com")
        with self.assertRaises(ValueError):
            self.facade.update_user(u2.id, {"email": "u1@x.com"})

    def test_update_user_own_email_ok(self):
        u = self._create("same@email.com")
        updated = self.facade.update_user(u.id, {"email": "same@email.com"})
        self.assertEqual(updated.email, "same@email.com")

    def test_update_nonexistent_user_returns_none(self):
        self.assertIsNone(self.facade.update_user("bad-id", {"first_name": "X"}))

    def test_to_dict_never_has_password(self):
        self.assertNotIn("password", self._create().to_dict())


if __name__ == "__main__":
    unittest.main(verbosity=2)
