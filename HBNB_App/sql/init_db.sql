-- =============================================================================
-- HBnB — Initialisation complète de la base de données
-- =============================================================================
-- Ce script regroupe la création du schéma ET l'insertion des données initiales.
-- Il remplace l'exécution séparée de schema.sql puis initial_data.sql.
--
-- Utilisation SQLite :
--   sqlite3 hbnb.db < init_db.sql
--
-- Utilisation MySQL :
--   mysql -u <user> -p <database> < init_db.sql
--
-- Compte administrateur par défaut :
--   Email    : admin@hbnb.io
--   Mot de passe : Admin1234!
-- =============================================================================

-- Activer les contraintes de clés étrangères (SQLite uniquement)
PRAGMA foreign_keys = ON;

-- =============================================================================
-- PARTIE 1 — SCHÉMA
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Table : users
-- Stocke les comptes utilisateurs (clients et administrateurs).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id          VARCHAR(36)  NOT NULL,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    first_name  VARCHAR(50)  NOT NULL,
    last_name   VARCHAR(50)  NOT NULL,
    email       VARCHAR(120) NOT NULL,
    password    VARCHAR(128) NOT NULL,   -- haché bcrypt, jamais en clair
    is_admin    BOOLEAN      NOT NULL DEFAULT 0,

    PRIMARY KEY (id),
    CONSTRAINT uq_users_email UNIQUE (email)
);

-- -----------------------------------------------------------------------------
-- Table : places
-- Représente les lieux mis en location par les propriétaires.
-- Un lieu appartient à un unique utilisateur (owner).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS places (
    id          VARCHAR(36)   NOT NULL,
    created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title       VARCHAR(100)  NOT NULL,
    description VARCHAR(1024),
    price       FLOAT         NOT NULL,
    latitude    FLOAT         NOT NULL,
    longitude   FLOAT         NOT NULL,
    owner_id    VARCHAR(36)   NOT NULL,

    PRIMARY KEY (id),
    CONSTRAINT fk_places_owner
        FOREIGN KEY (owner_id) REFERENCES users(id)
        ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- Table : amenities
-- Catalogue des équipements disponibles (Wi-Fi, piscine, etc.).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS amenities (
    id         VARCHAR(36) NOT NULL,
    created_at DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name       VARCHAR(50) NOT NULL,

    PRIMARY KEY (id)
);

-- -----------------------------------------------------------------------------
-- Table : reviews
-- Avis laissés par les utilisateurs sur les lieux.
-- Un avis est lié à un lieu ET à un utilisateur.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reviews (
    id         VARCHAR(36)   NOT NULL,
    created_at DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    text       VARCHAR(2048) NOT NULL,
    rating     INTEGER       NOT NULL
                             CHECK (rating BETWEEN 1 AND 5),
    place_id   VARCHAR(36)   NOT NULL,
    user_id    VARCHAR(36)   NOT NULL,

    PRIMARY KEY (id),
    CONSTRAINT fk_reviews_place
        FOREIGN KEY (place_id) REFERENCES places(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_reviews_user
        FOREIGN KEY (user_id)  REFERENCES users(id)
        ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- Table : place_amenity  (table pivot many-to-many Place <-> Amenity)
-- Un lieu peut avoir plusieurs équipements ; un équipement peut être dans
-- plusieurs lieux.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS place_amenity (
    place_id   VARCHAR(36) NOT NULL,
    amenity_id VARCHAR(36) NOT NULL,

    PRIMARY KEY (place_id, amenity_id),
    CONSTRAINT fk_pa_place
        FOREIGN KEY (place_id)   REFERENCES places(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_pa_amenity
        FOREIGN KEY (amenity_id) REFERENCES amenities(id)
        ON DELETE CASCADE
);

-- =============================================================================
-- PARTIE 2 — DONNÉES INITIALES
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Utilisateur administrateur
-- is_admin = 1  →  identifiant administrateur en base
-- Mot de passe : Admin1234!
-- Hash bcrypt généré avec bcrypt.hashpw('Admin1234!', bcrypt.gensalt(12))
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
