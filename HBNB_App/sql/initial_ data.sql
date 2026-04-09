-- =============================================================================
-- HBnB — Données initiales
-- =============================================================================
-- Ce script insère les données minimales requises au démarrage :
--   1. Un utilisateur administrateur
--   2. Un catalogue d'équipements (amenities) courants
--
-- PRÉREQUIS : exécuter schema.sql avant ce script.
--
-- Utilisation SQLite :
--   sqlite3 hbnb.db < initial_data.sql
--
-- Utilisation MySQL :
--   mysql -u <user> -p <database> < initial_data.sql
--
-- Mot de passe admin : Admin1234!
-- Hash bcrypt généré avec bcrypt.hashpw('Admin1234!', bcrypt.gensalt(12))
-- =============================================================================

PRAGMA foreign_keys = ON;

-- -----------------------------------------------------------------------------
-- Utilisateur administrateur
-- -----------------------------------------------------------------------------
INSERT OR IGNORE INTO users (
    id,
    created_at,
    updated_at,
    first_name,
    last_name,
    email,
    password,
    is_admin
) VALUES (
    'd2d3fe8a-4eaa-4aff-97e4-8fcf989c2f47',
    '2026-03-17 10:20:42',
    '2026-03-17 10:20:42',
    'Admin',
    'HBnB',
    'admin@hbnb.io',
    '$2b$12$SinqIar/tNnFyM4V0V54DeHZ9tBRZ2hCcBOyiykQTuAYA1TDieQPC',
    1
);

-- -----------------------------------------------------------------------------
-- Équipements (amenities)
-- -----------------------------------------------------------------------------
INSERT OR IGNORE INTO amenities (id, created_at, updated_at, name) VALUES
    ('5fc4aed6-4d38-400b-88cd-c4a55314d3af', '2026-03-17 10:20:42', '2026-03-17 10:20:42', 'Wi-Fi'),
    ('2d86c522-1654-47db-b8e5-f7a931ed449c', '2026-03-17 10:20:42', '2026-03-17 10:20:42', 'Piscine'),
    ('3000988a-e7b0-4b2d-bde5-6b6a0e38e0cb', '2026-03-17 10:20:42', '2026-03-17 10:20:42', 'Climatisation'),
    ('247360fb-1574-4f6c-b42c-808b48a0b2d5', '2026-03-17 10:20:42', '2026-03-17 10:20:42', 'Parking'),
    ('0e9ca294-a1d9-4721-8107-390c17a21baf', '2026-03-17 10:20:42', '2026-03-17 10:20:42', 'Cuisine équipée'),
    ('84a4edd6-6838-4e75-92c5-13159800856d', '2026-03-17 10:20:42', '2026-03-17 10:20:42', 'Salle de sport');