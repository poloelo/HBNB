#!/usr/bin/env python3
"""
Script de données de test pour HBnB.
Usage : cd HBNB_App && python seed.py

Crée :
  - 2 utilisateurs (Alice, Bob)
  - 3 places avec images SVG fournies
  - 3 reviews croisées
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.services import facade
from app.extensions import db

app = create_app()

# ── IDs des amenities insérés par initial_data.sql ────────────────────────────
WIFI       = '5fc4aed6-4d38-400b-88cd-c4a55314d3af'
POOL       = '2d86c522-1654-47db-b8e5-f7a931ed449c'
AC         = '3000988a-e7b0-4b2d-bde5-6b6a0e38e0cb'
PARKING    = '247360fb-1574-4f6c-b42c-808b48a0b2d5'
KITCHEN    = '0e9ca294-a1d9-4721-8107-390c17a21baf'
GYM        = '84a4edd6-6838-4e75-92c5-13159800856d'
ADMIN_ID   = 'd2d3fe8a-4eaa-4aff-97e4-8fcf989c2f47'

with app.app_context():

    # ── Utilisateurs ──────────────────────────────────────────────────────────
    alice = facade.get_user_by_email('alice@hbnb.io')
    if not alice:
        alice = facade.create_user({
            'first_name': 'Alice',
            'last_name':  'Martin',
            'email':      'alice@hbnb.io',
            'password':   'Alice1234!',
            'is_admin':   False,
        })
        print(f"Utilisateur créé : Alice Martin  ({alice.id})")
    else:
        print(f"Alice existe déjà ({alice.id})")

    bob = facade.get_user_by_email('bob@hbnb.io')
    if not bob:
        bob = facade.create_user({
            'first_name': 'Bob',
            'last_name':  'Dupont',
            'email':      'bob@hbnb.io',
            'password':   'Bob1234!',
            'is_admin':   False,
        })
        print(f"Utilisateur créé : Bob Dupont  ({bob.id})")
    else:
        print(f"Bob existe déjà ({bob.id})")

    # ── Places ────────────────────────────────────────────────────────────────
    existing_places = {p.title for p in facade.get_all_places()}

    if "Appartement cosy à Paris" not in existing_places:
        p1 = facade.create_place({
            'title':       "Appartement cosy à Paris",
            'description': "Beau studio lumineux au cœur du Marais, à deux pas des musées et des meilleures boulangeries de Paris. Calme et confortable.",
            'price':       90.0,
            'latitude':    48.8566,
            'longitude':   2.3522,
            'owner_id':    alice.id,
            'amenities':   [WIFI, KITCHEN],
        })
        facade.update_place(p1.id, {'image_filename': 'images/place1.svg'})
        print(f"Place créée : {p1.title} ({p1.id})")
    else:
        p1 = next(p for p in facade.get_all_places() if p.title == "Appartement cosy à Paris")
        print(f"Place existe déjà : {p1.title}")

    if "Villa avec piscine à Nice" not in existing_places:
        p2 = facade.create_place({
            'title':       "Villa avec piscine à Nice",
            'description': "Magnifique villa provençale avec piscine privée et vue mer. Idéale pour les vacances en famille ou entre amis sur la Côte d'Azur.",
            'price':       250.0,
            'latitude':    43.7102,
            'longitude':   7.2620,
            'owner_id':    bob.id,
            'amenities':   [WIFI, POOL, AC, PARKING],
        })
        facade.update_place(p2.id, {'image_filename': 'images/place2.svg'})
        print(f"Place créée : {p2.title} ({p2.id})")
    else:
        p2 = next(p for p in facade.get_all_places() if p.title == "Villa avec piscine à Nice")
        print(f"Place existe déjà : {p2.title}")

    if "Chalet en montagne" not in existing_places:
        p3 = facade.create_place({
            'title':       "Chalet en montagne",
            'description': "Chalet authentique dans les Alpes avec vue imprenable sur les sommets. Parfait pour le ski en hiver et les randonnées en été.",
            'price':       120.0,
            'latitude':    45.1885,
            'longitude':   5.7245,
            'owner_id':    alice.id,
            'amenities':   [WIFI, PARKING, KITCHEN],
        })
        facade.update_place(p3.id, {'image_filename': 'images/place3.svg'})
        print(f"Place créée : {p3.title} ({p3.id})")
    else:
        p3 = next(p for p in facade.get_all_places() if p.title == "Chalet en montagne")
        print(f"Place existe déjà : {p3.title}")

    # ── Reviews ───────────────────────────────────────────────────────────────
    def add_review_if_not_exists(user_id, place_id, text, rating):
        existing = facade.get_review_by_user_and_place(user_id, place_id)
        if not existing:
            r = facade.create_review({
                'user_id':  user_id,
                'place_id': place_id,
                'text':     text,
                'rating':   rating,
            })
            print(f"Review créée : {rating}★ sur {place_id[:8]}...")
        else:
            print(f"Review existe déjà pour {place_id[:8]}...")

    # Bob commente l'appartement d'Alice
    add_review_if_not_exists(
        bob.id, p1.id,
        "Super appartement, très bien situé et parfaitement équipé. Alice est une hôte attentionnée. Je recommande vivement !",
        5
    )

    # Alice commente la villa de Bob
    add_review_if_not_exists(
        alice.id, p2.id,
        "La villa est encore plus belle qu'en photos. La piscine est top, le quartier calme. On reviendra l'année prochaine !",
        4
    )

    # Admin commente le chalet d'Alice (avec son ID fixe)
    add_review_if_not_exists(
        ADMIN_ID, p3.id,
        "Chalet authentique et bien équipé. Vue magnifique depuis la terrasse. Parfait pour se ressourcer en montagne.",
        5
    )

    print("\n✓ Données de test insérées avec succès !")
    print("\nComptes disponibles :")
    print(f"  admin@hbnb.io   / Admin1234!  (administrateur)")
    print(f"  alice@hbnb.io   / Alice1234!")
    print(f"  bob@hbnb.io     / Bob1234!")
