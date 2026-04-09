-- =============================================================================
-- HBnB — Schéma de la base de données
-- =============================================================================
-- Ce script crée toutes les tables nécessaires à l'application HBnB.
-- Il peut être exécuté sur une base SQLite ou MySQL/MariaDB.
--
-- Utilisation SQLite :
--   sqlite3 hbnb.db < schema.sql
--
-- Utilisation MySQL :
--   mysql -u <user> -p <database> < schema.sql
-- =============================================================================

-- Activer les contraintes de clés étrangères (SQLite uniquement)
PRAGMA foreign_keys = ON;

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