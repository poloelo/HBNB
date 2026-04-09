<div align="center">

# 🏠 AirBnB Clone — *hbnb*

> Reproduction full-stack de la plateforme AirBnB : CLI, stockage JSON/MySQL, API REST et rendu web dynamique.

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Style: pycodestyle](https://img.shields.io/badge/code%20style-pycodestyle-blue?style=flat-square)](https://pycodestyle.pycqa.org/)
[![Tests: unittest](https://img.shields.io/badge/tests-unittest-green?style=flat-square)](https://docs.python.org/3/library/unittest.html)

</div>

---

## 📋 Table des matières

- [Description](#-description)
- [Fonctionnalités](#-fonctionnalités)
- [Technologies utilisées](#-technologies-utilisées)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Structure du projet](#-structure-du-projet)
- [Diagramme Entité-Relation (ER)](#-diagramme-entité-relation-er)
- [Documentation du code](#-documentation-du-code)
- [Tests](#-tests)
- [Stratégie de branches](#-stratégie-de-branches)
- [Captures d'écran](#-captures-décran)
- [Contributions](#-contributions)
- [Auteure](#-auteure)

---

## 📖 Description

**hbnb** est un clone de la plateforme AirBnB développé en plusieurs phases à Holberton School.  
Le projet couvre l'intégralité de la chaîne : modèles orientés objet, persistance des données (JSON puis MySQL), interface en ligne de commande, API REST sécurisée et rendu HTML dynamique via Flask.

**Objectifs pédagogiques :**
- Maîtriser la programmation orientée objet en Python
- Comprendre les patterns de stockage et l'abstraction des données
- Construire et consommer une API REST
- Déployer une application web avec Flask + Jinja2

---

## ✨ Fonctionnalités

| Fonctionnalité | Détail |
|:---|:---|
| 🧱 **Modèles OOP** | `User`, `Place`, `Review`, `Amenity`, `City`, `State` héritent de `BaseModel` |
| 💾 **Stockage dual** | `FileStorage` (JSON) → `DBStorage` (MySQL via SQLAlchemy) |
| 🖥️ **Console interactive** | Commandes `create`, `show`, `update`, `destroy`, `all`, `count` |
| 🌐 **Rendu web** | Templates HTML dynamiques avec Flask + Jinja2 |
| 🔌 **API REST** | Endpoints JSON conformes REST (GET, POST, PUT, DELETE) |
| 🧪 **Tests unitaires** | Couverture `unittest` sur tous les modèles et moteurs de stockage |

---

## 🛠️ Technologies utilisées

| Catégorie | Technologie | Version |
|:---|:---|:---:|
| Langage | Python | 3.8+ |
| Framework web | Flask | 2.x |
| ORM | SQLAlchemy | 1.4+ |
| Base de données | MySQL | 8.0 |
| Sérialisation | JSON (stdlib) | — |
| Templating | Jinja2 | 3.x |
| Linter | pycodestyle | 2.8+ |
| Tests | unittest (stdlib) | — |
| Versioning | Git / GitHub | — |

---

## ⚙️ Prérequis

- **OS :** Ubuntu 20.04 LTS (recommandé) ou macOS 12+
- **Python :** 3.8 ou supérieur
- **MySQL :** 8.0 (pour le mode DBStorage uniquement)
- **pip :** 21+

Vérifiez vos versions :

```bash
python3 --version   # Python 3.8+
pip3 --version      # pip 21+
mysql --version     # mysql  Ver 8.0 (optionnel)
```

---

## 🚀 Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/sam99-web/AirBnB_clone.git
cd AirBnB_clone
```

### 2. Créer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. (Optionnel) Configurer MySQL pour DBStorage

```bash
# Créer la base de données et l'utilisateur
mysql -u root -p < setup_mysql_dev.sql

# Variables d'environnement requises
export HBNB_MYSQL_USER=hbnb_dev
export HBNB_MYSQL_PWD=hbnb_dev_pwd
export HBNB_MYSQL_HOST=localhost
export HBNB_MYSQL_DB=hbnb_dev_db
export HBNB_TYPE_STORAGE=db
```

---

## 💻 Utilisation

### Console interactive

```bash
./console.py
```

#### Exemples de commandes

```bash
# Créer un utilisateur
(hbnb) create User email="alice@mail.com" password="1234" first_name="Alice"

# Afficher tous les objets d'un type
(hbnb) all User

# Afficher un objet précis
(hbnb) show User <id>

# Mettre à jour un attribut
(hbnb) update User <id> first_name "Bob"

# Supprimer un objet
(hbnb) destroy User <id>

# Compter les instances
(hbnb) User.count()

# Quitter la console
(hbnb) quit
```

### Lancer le serveur web (Flask)

```bash
python3 -m web_flask.0-hello_route
# Accessible sur http://0.0.0.0:5000/
```

### Lancer l'API REST

```bash
python3 -m api.v1.app
# Accessible sur http://0.0.0.0:5000/api/v1/
```

Exemple d'appel API :

```bash
# Récupérer toutes les villes
curl http://0.0.0.0:5000/api/v1/cities

# Créer un état
curl -X POST http://0.0.0.0:5000/api/v1/states \
     -H "Content-Type: application/json" \
     -d '{"name": "California"}'
```

---

## 📁 Structure du projet

```
AirBnB_clone/
├── models/                  # Modèles OOP et moteurs de stockage
│   ├── base_model.py        # Classe de base (id, created_at, updated_at)
│   ├── user.py
│   ├── place.py
│   ├── review.py
│   ├── amenity.py
│   ├── city.py
│   ├── state.py
│   └── engine/
│       ├── file_storage.py  # Stockage JSON
│       └── db_storage.py    # Stockage MySQL via SQLAlchemy
├── api/
│   └── v1/
│       ├── app.py           # Point d'entrée Flask API
│       └── views/           # Blueprints REST
├── web_flask/               # Application web Flask + Jinja2
├── web_static/              # Assets statiques (HTML/CSS)
├── tests/                   # Tests unitaires
│   └── test_models/
├── console.py               # CLI interactive
├── requirements.txt
└── README.md
```

---

## 🗂️ Diagramme Entité-Relation (ER)

Schéma de la base de données HBnB représenté avec [Mermaid.js](https://mermaid.js.org/).

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

### Relations

| Relation | Type | Description |
|---|---|---|
| `users` → `places` | One-to-Many | Un utilisateur possède zéro ou plusieurs lieux |
| `users` → `reviews` | One-to-Many | Un utilisateur rédige zéro ou plusieurs avis |
| `places` → `reviews` | One-to-Many | Un lieu reçoit zéro ou plusieurs avis |
| `places` ↔ `amenities` | Many-to-Many | Via la table pivot `place_amenity` |

### Contraintes

- Toutes les suppressions se propagent en cascade (`ON DELETE CASCADE`)
- `users.email` : unique
- `amenities.name` : unique
- `reviews.rating` : entier entre 1 et 5 (`CHECK`)
- Clés primaires : UUID v4 (VARCHAR 36)

---

## 📚 Documentation du code

Le code suit le standard **PEP 257** pour les docstrings Python.  
Chaque module, classe et méthode est documenté selon ce format :

```python
def save(self):
    """Sérialise toutes les instances dans le fichier JSON.

    Converts all stored BaseModel instances to their dictionary
    representation and writes them to the JSON file path.
    """
```

Le respect du style est vérifié avec **pycodestyle** :

```bash
pycodestyle models/ api/ web_flask/ console.py
```

---

## 🧪 Tests

Les tests unitaires couvrent tous les modèles et les deux moteurs de stockage.

```bash
# Lancer tous les tests
python3 -m unittest discover tests

# Tester un module spécifique
python3 -m unittest tests.test_models.test_base_model

# Avec FileStorage
HBNB_TYPE_STORAGE=file python3 -m unittest discover tests

# Avec DBStorage
HBNB_TYPE_STORAGE=db python3 -m unittest discover tests
```

---

## 🌿 Stratégie de branches

| Branche | Rôle |
|:---|:---|
| `main` | Code stable — déploiement / production |
| `dev` | Développement actif des nouvelles fonctionnalités |
| `tests` | Intégration et validation des tests unitaires |

**Conventions de commit :**

```
feat: ajouter le moteur DBStorage avec SQLAlchemy
fix: corriger la sérialisation des dates dans FileStorage
docs: mettre à jour le README avec les exemples d'API
test: ajouter les tests unitaires pour le modèle Place
refactor: renommer get_all en retrieve_all dans db_storage
```

---

## 📸 Captures d'écran

### Console interactive
```
$ ./console.py
(hbnb) create User email="test@mail.com" password="pwd"
246c227a-6b9b-4f3b-9a2e-b4c123456789
(hbnb) show User 246c227a-6b9b-4f3b-9a2e-b4c123456789
[User] (246c227a...) {'id': '246c...', 'email': 'test@mail.com', ...}
(hbnb)
```

---

## 🤝 Contributions

Les contributions sont les bienvenues !

1. Forkez le dépôt
2. Créez une branche feature : `git checkout -b feat/ma-fonctionnalite`
3. Committez vos changements : `git commit -m "feat: ajouter ma fonctionnalité"`
4. Poussez la branche : `git push origin feat/ma-fonctionnalite`
5. Ouvrez une Pull Request vers `dev`

**Remerciements :** Holberton School pour le cadre pédagogique et la communauté des étudiants pour les échanges et révisions de code.

---

## 👩🏾‍💻 Auteure

Ndeye Fatou Samb  and PAUL GLORIA
📍 Montargis, France  
📧 [keishsam99@gmail.com](mailto:keishsam99@gmail.com)  
🐙 [github.com/sam99-web](https://github.com/sam99-web)

---

<div align="center">

*"The only way to learn a new programming language is by writing programs in it."* — Dennis Ritchie

</div>
