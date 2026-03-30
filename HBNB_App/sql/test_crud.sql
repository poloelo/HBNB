-- =============================================================================
-- HBnB — Tests CRUD
-- =============================================================================
-- Ce script valide le bon fonctionnement du schéma en testant toutes les
-- opérations CRUD (Create, Read, Update, Delete) sur chaque table.
--
-- PRÉREQUIS : exécuter schema.sql puis initial_data.sql avant ce script.
--
-- Utilisation SQLite :
--   sqlite3 hbnb.db < test_crud.sql
-- =============================================================================

PRAGMA foreign_keys = ON;

-- =============================================================================
-- 1. CREATE — Insertions
-- =============================================================================

-- Utilisateur standard
INSERT INTO users (id, created_at, updated_at, first_name, last_name, email, password, is_admin)
VALUES (
    'aaaaaaaa-0000-0000-0000-000000000001',
    '2026-01-01 00:00:00',
    '2026-01-01 00:00:00',
    'Alice',
    'Dupont',
    'alice@example.com',
    '$2b$12$fakehashfortest000000000000000000000000000000000000000',
    0
);

-- Second utilisateur (pour tester les reviews)
INSERT INTO users (id, created_at, updated_at, first_name, last_name, email, password, is_admin)
VALUES (
    'aaaaaaaa-0000-0000-0000-000000000002',
    '2026-01-01 00:00:00',
    '2026-01-01 00:00:00',
    'Bob',
    'Martin',
    'bob@example.com',
    '$2b$12$fakehashfortest000000000000000000000000000000000000001',
    0
);

-- Lieu appartenant à Alice
INSERT INTO places (id, created_at, updated_at, title, description, price, latitude, longitude, owner_id)
VALUES (
    'bbbbbbbb-0000-0000-0000-000000000001',
    '2026-01-01 00:00:00',
    '2026-01-01 00:00:00',
    'Studio Paris Centre',
    'Beau studio en plein coeur de Paris.',
    85.0,
    48.8566,
    2.3522,
    'aaaaaaaa-0000-0000-0000-000000000001'
);

-- Amenity de test
INSERT OR IGNORE INTO amenities (id, created_at, updated_at, name)
VALUES (
    'cccccccc-0000-0000-0000-000000000001',
    '2026-01-01 00:00:00',
    '2026-01-01 00:00:00',
    'Télévision'
);

-- Liaison Place ↔ Amenity
INSERT INTO place_amenity (place_id, amenity_id)
VALUES (
    'bbbbbbbb-0000-0000-0000-000000000001',
    'cccccccc-0000-0000-0000-000000000001'
);

-- Review de Bob sur le lieu d'Alice (Bob ne peut pas reviewer son propre lieu)
INSERT INTO reviews (id, created_at, updated_at, text, rating, place_id, user_id)
VALUES (
    'dddddddd-0000-0000-0000-000000000001',
    '2026-01-01 00:00:00',
    '2026-01-01 00:00:00',
    'Très bel endroit, propre et bien situé.',
    5,
    'bbbbbbbb-0000-0000-0000-000000000001',
    'aaaaaaaa-0000-0000-0000-000000000002'
);

-- Vérification : contrainte CHECK rating (doit échouer si décommenté)
-- INSERT INTO reviews (id, created_at, updated_at, text, rating, place_id, user_id)
-- VALUES ('bad-review', '2026-01-01', '2026-01-01', 'Test', 6,
--         'bbbbbbbb-0000-0000-0000-000000000001', 'aaaaaaaa-0000-0000-0000-000000000002');


-- =============================================================================
-- 2. READ — Lectures
-- =============================================================================

-- Tous les utilisateurs
SELECT 'READ users' AS test;
SELECT id, first_name, last_name, email, is_admin FROM users;

-- Tous les lieux avec le nom du propriétaire
SELECT 'READ places + owner' AS test;
SELECT p.id, p.title, p.price, u.email AS owner_email
FROM places p
JOIN users u ON p.owner_id = u.id;

-- Amenities d'un lieu
SELECT 'READ amenities of place' AS test;
SELECT a.name
FROM amenities a
JOIN place_amenity pa ON pa.amenity_id = a.id
WHERE pa.place_id = 'bbbbbbbb-0000-0000-0000-000000000001';

-- Toutes les reviews avec auteur et lieu
SELECT 'READ reviews + user + place' AS test;
SELECT r.id, r.rating, r.text, u.email AS author, p.title AS place
FROM reviews r
JOIN users u ON r.user_id = u.id
JOIN places p ON r.place_id = p.id;

-- Vérification unicité email (doit retourner 1 ligne par email)
SELECT 'READ email uniqueness' AS test;
SELECT email, COUNT(*) AS nb FROM users GROUP BY email;


-- =============================================================================
-- 3. UPDATE — Mises à jour
-- =============================================================================

-- Modifier le prix du lieu
SELECT 'UPDATE place price' AS test;
UPDATE places
SET price = 95.0, updated_at = '2026-02-01 00:00:00'
WHERE id = 'bbbbbbbb-0000-0000-0000-000000000001';

SELECT title, price FROM places WHERE id = 'bbbbbbbb-0000-0000-0000-000000000001';

-- Modifier la note d'une review
SELECT 'UPDATE review rating' AS test;
UPDATE reviews
SET rating = 4, updated_at = '2026-02-01 00:00:00'
WHERE id = 'dddddddd-0000-0000-0000-000000000001';

SELECT text, rating FROM reviews WHERE id = 'dddddddd-0000-0000-0000-000000000001';

-- Modifier le prénom d'un utilisateur
SELECT 'UPDATE user first_name' AS test;
UPDATE users
SET first_name = 'Alicia', updated_at = '2026-02-01 00:00:00'
WHERE id = 'aaaaaaaa-0000-0000-0000-000000000001';

SELECT first_name, last_name FROM users WHERE id = 'aaaaaaaa-0000-0000-0000-000000000001';


-- =============================================================================
-- 4. DELETE — Suppressions (avec vérification des cascades)
-- =============================================================================

-- Supprimer la review directement
SELECT 'DELETE review' AS test;
DELETE FROM reviews WHERE id = 'dddddddd-0000-0000-0000-000000000001';
SELECT COUNT(*) AS reviews_restantes FROM reviews;

-- Supprimer le lieu → doit supprimer les lignes de place_amenity en cascade
SELECT 'DELETE place (cascade place_amenity)' AS test;
DELETE FROM places WHERE id = 'bbbbbbbb-0000-0000-0000-000000000001';
SELECT COUNT(*) AS place_amenity_restantes FROM place_amenity
WHERE place_id = 'bbbbbbbb-0000-0000-0000-000000000001';

-- Supprimer Alice → doit supprimer ses lieux et reviews en cascade
-- (Les lieux d'Alice ont déjà été supprimés ci-dessus)
SELECT 'DELETE user Alice' AS test;
DELETE FROM users WHERE id = 'aaaaaaaa-0000-0000-0000-000000000001';
SELECT COUNT(*) AS users_restants FROM users WHERE id = 'aaaaaaaa-0000-0000-0000-000000000001';

-- Supprimer Bob
DELETE FROM users WHERE id = 'aaaaaaaa-0000-0000-0000-000000000002';

-- Supprimer l'amenity de test (ne supprime PAS les lieux grâce au cascade côté amenity)
DELETE FROM amenities WHERE id = 'cccccccc-0000-0000-0000-000000000001';

-- Vérification finale : seuls les données de initial_data.sql restent
SELECT 'FINAL STATE — users' AS test;
SELECT email, is_admin FROM users;

SELECT 'FINAL STATE — amenities' AS test;
SELECT name FROM amenities;
