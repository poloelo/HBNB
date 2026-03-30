# HBnB — Diagramme Entité-Relation (ER)

Schéma de la base de données HBnB représenté avec [Mermaid.js](https://mermaid.js.org/).

## Diagramme ER

```mermaid
erDiagram
    users {
        VARCHAR(36)  id          PK
        DATETIME     created_at
        DATETIME     updated_at
        VARCHAR(50)  first_name
        VARCHAR(50)  last_name
        VARCHAR(120) email       UK
        VARCHAR(128) password
        BOOLEAN      is_admin
    }

    places {
        VARCHAR(36)   id          PK
        DATETIME      created_at
        DATETIME      updated_at
        VARCHAR(100)  title
        VARCHAR(1024) description
        FLOAT         price
        FLOAT         latitude
        FLOAT         longitude
        VARCHAR(36)   owner_id    FK
    }

    amenities {
        VARCHAR(36) id         PK
        DATETIME    created_at
        DATETIME    updated_at
        VARCHAR(50) name       UK
    }

    reviews {
        VARCHAR(36)   id         PK
        DATETIME      created_at
        DATETIME      updated_at
        VARCHAR(2048) text
        INTEGER       rating
        VARCHAR(36)   place_id   FK
        VARCHAR(36)   user_id    FK
    }

    place_amenity {
        VARCHAR(36) place_id   FK
        VARCHAR(36) amenity_id FK
    }

    users   ||--o{ places       : "possède (owner_id)"
    users   ||--o{ reviews      : "rédige (user_id)"
    places  ||--o{ reviews      : "reçoit (place_id)"
    places  }o--o{ amenities    : "dispose de"
    places  ||--o{ place_amenity : ""
    amenities ||--o{ place_amenity : ""
```

## Relations

| Relation | Type | Description |
|---|---|---|
| `users` → `places` | One-to-Many | Un utilisateur possède zéro ou plusieurs lieux |
| `users` → `reviews` | One-to-Many | Un utilisateur rédige zéro ou plusieurs avis |
| `places` → `reviews` | One-to-Many | Un lieu reçoit zéro ou plusieurs avis |
| `places` ↔ `amenities` | Many-to-Many | Via la table pivot `place_amenity` |

## Contraintes

- Toutes les suppressions se propagent en cascade (`ON DELETE CASCADE`)
- `users.email` : unique
- `amenities.name` : unique
- `reviews.rating` : entier entre 1 et 5 (`CHECK`)
- Clés primaires : UUID v4 (VARCHAR 36)
