"""
seed_mock.py — Données de test (Mock Data)
==========================================
Peuple la base de données avec :
  - 5 utilisateurs fictifs
  - 8 lieux (places) avec équipements
  - 18 avis (reviews) en respectant toutes les contraintes :
      • Un utilisateur ne peut pas évaluer son propre lieu
      • Une seule review par (utilisateur, lieu)
      • rating entre 1 et 5

Utilisation :
    cd HBNB_App
    python seed_mock.py
"""

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity

app = create_app()

with app.app_context():

    # ── Garde-fou : ne pas re-seeder si déjà fait ──────────────────────────────
    if User.query.filter_by(email="marie.dupont@test.com").first():
        print("ℹ️  Les données de test existent déjà — rien à faire.")
        exit(0)

    print("🌱 Création des données de test...")

    # ── 1. Utilisateurs ────────────────────────────────────────────────────────
    users = [
        User(first_name="Marie",  last_name="Dupont",  email="marie.dupont@test.com",   password="Password1!"),
        User(first_name="Jean",   last_name="Martin",  email="jean.martin@test.com",    password="Password1!"),
        User(first_name="Sophie", last_name="Bernard", email="sophie.bernard@test.com", password="Password1!"),
        User(first_name="Lucas",  last_name="Petit",   email="lucas.petit@test.com",    password="Password1!"),
        User(first_name="Emma",   last_name="Leroy",   email="emma.leroy@test.com",     password="Password1!"),
    ]
    for u in users:
        db.session.add(u)
    db.session.flush()  # génère les UUIDs sans commit

    marie, jean, sophie, lucas, emma = users

    # ── 2. Équipements (déjà présents via seed.py / init_db.sql) ──────────────
    def get_amenity(name):
        return Amenity.query.filter_by(name=name).first()

    wifi    = get_amenity("Wi-Fi")
    piscine = get_amenity("Piscine")
    clim    = get_amenity("Climatisation")
    parking = get_amenity("Parking")
    cuisine = get_amenity("Cuisine équipée")
    sport   = get_amenity("Salle de sport")

    # ── 3. Lieux ───────────────────────────────────────────────────────────────
    def make_place(title, desc, price, lat, lng, owner, amenities):
        p = Place(
            title=title,
            description=desc,
            price=price,
            latitude=lat,
            longitude=lng,
            owner_id=owner.id,
        )
        for a in amenities:
            if a:
                p.add_amenity(a)
        return p

    places = [
        # ── Marie (2 lieux) ────────────────────────────────────────────────────
        make_place(
            "Loft parisien moderne",
            "Superbe loft lumineux au cœur de Paris, proche de tous les transports. "
            "Design contemporain avec vue sur les toits.",
            85.0, 48.8566, 2.3522, marie, [wifi, clim],
        ),
        make_place(
            "Studio cosy Lyon",
            "Studio chaleureux dans le vieux Lyon. Idéal pour découvrir la capitale "
            "de la gastronomie française.",
            45.0, 45.7640, 4.8357, marie, [wifi, parking],
        ),
        # ── Jean (2 lieux) ─────────────────────────────────────────────────────
        make_place(
            "Villa provençale avec piscine",
            "Magnifique villa en Provence avec grande piscine privée, jardin et vue sur "
            "les Alpilles. Parfaite pour les familles.",
            150.0, 43.9493, 4.8055, jean, [wifi, piscine, clim, parking, cuisine],
        ),
        make_place(
            "Appartement centre Bordeaux",
            "Appartement haussmannien rénové en plein cœur de Bordeaux, à deux pas "
            "des quais et de la place de la Bourse.",
            65.0, 44.8378, -0.5792, jean, [wifi, parking],
        ),
        # ── Sophie (2 lieux) ───────────────────────────────────────────────────
        make_place(
            "Chalet des Alpes",
            "Chalet d'exception avec vue panoramique sur le Mont-Blanc. "
            "Sauna, spa et accès direct aux pistes de ski.",
            200.0, 45.9237, 6.8694, sophie, [wifi, cuisine, sport],
        ),
        make_place(
            "Maison bretonne avec jardin",
            "Maison typique bretonne avec grand jardin clos. "
            "Atmosphère authentique à 5 min des plages.",
            95.0, 48.1173, -1.6778, sophie, [wifi, parking, cuisine],
        ),
        # ── Lucas (1 lieu) ─────────────────────────────────────────────────────
        make_place(
            "Gîte normand authentique",
            "Ancien corps de ferme normand restauré. Calme absolu, grand terrain, "
            "idéal pour se ressourcer à la campagne.",
            55.0, 49.1829, -0.3707, lucas, [wifi, cuisine],
        ),
        # ── Emma (1 lieu) ──────────────────────────────────────────────────────
        make_place(
            "Cabane dans les arbres",
            "Cabane perchée unique dans une forêt de chênes centenaires. "
            "Expérience magique, déconnectez-vous du quotidien !",
            120.0, 44.6333, 0.5833, emma, [wifi, cuisine],
        ),
    ]
    for p in places:
        db.session.add(p)
    db.session.flush()

    p_loft, p_studio, p_villa, p_bordeaux, p_chalet, p_bretagne, p_gite, p_cabane = places

    # ── 4. Avis ────────────────────────────────────────────────────────────────
    # Contraintes respectées :
    #   - owner != reviewer
    #   - (reviewer, place) unique
    reviews_data = [
        # Loft parisien — owner: marie
        (jean,   p_loft,     5, "Magnifique loft, parfaitement situé et très lumineux. On s'y sent comme chez soi !"),
        (sophie, p_loft,     4, "Très bel espace, propre et moderne. Hôte très réactif. Je recommande vivement."),
        (lucas,  p_loft,     5, "Parfait pour un séjour parisien. Le quartier est vivant et bien desservi."),
        # Studio Lyon — owner: marie
        (jean,   p_studio,   4, "Petit studio mais très bien agencé et pratique. Idéalement placé dans le vieux Lyon."),
        (emma,   p_studio,   3, "Correct pour un court séjour. Un peu petit mais bien équipé."),
        # Villa provençale — owner: jean
        (marie,  p_villa,    5, "Villa de rêve absolue ! La piscine, le jardin, la vue... on ne voulait plus partir."),
        (sophie, p_villa,    5, "Séjour inoubliable ! La villa est encore plus belle en vrai. On reviendra sûrement."),
        (emma,   p_villa,    4, "Superbe villa, piscine impeccable et vue magnifique sur les Alpilles."),
        # Bordeaux — owner: jean
        (marie,  p_bordeaux, 4, "Superbe emplacement en plein cœur de Bordeaux. Appartement élégant et bien équipé."),
        (lucas,  p_bordeaux, 3, "Bien situé mais l'isolation phonique laisse à désirer la nuit."),
        # Chalet Alpes — owner: sophie
        (marie,  p_chalet,   5, "Chalet de luxe avec une vue à couper le souffle ! Le sauna après le ski, c'est parfait."),
        (jean,   p_chalet,   5, "Incroyable séjour ! Le meilleur endroit où j'aie jamais séjourné. Merci Sophie !"),
        (emma,   p_chalet,   4, "Très beau chalet, tout le confort pour un séjour au ski."),
        # Maison bretonne — owner: sophie
        (jean,   p_bretagne, 4, "Maison charmante avec un beau jardin. Très bon accueil et ambiance authentique."),
        (lucas,  p_bretagne, 4, "Très agréable séjour en Bretagne. La maison est typique et bien équipée."),
        # Gîte normand — owner: lucas
        (marie,  p_gite,     4, "Gîte authentique et très reposant. Dépaysement total, idéal pour recharger les batteries."),
        (sophie, p_gite,     3, "Calme et nature, parfait pour se ressourcer. Un peu isolé mais c'est le but."),
        # Cabane dans les arbres — owner: emma
        (jean,   p_cabane,   5, "Expérience unique et féérique dans les arbres ! Les enfants étaient ravis."),
        (lucas,  p_cabane,   5, "Incroyable ! Nuit sous les étoiles, réveil dans les arbres... Un souvenir inoubliable."),
    ]

    for author, place, rating, text in reviews_data:
        r = Review(text=text, rating=rating, place_id=place.id, user_id=author.id)
        db.session.add(r)

    db.session.commit()

    print(f"✅  {len(users)} utilisateurs créés")
    print(f"✅  {len(places)} lieux créés")
    print(f"✅  {len(reviews_data)} avis créés")
    print()
    print("📋 Comptes de test (mot de passe : Password1!) :")
    for u in users:
        print(f"   {u.email}")
