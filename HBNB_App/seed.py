from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()

with app.app_context():
    db.create_all()
    existing = User.query.filter_by(email="admin@hbnb.io").first()
    if not existing:
        admin = User(
            first_name="Admin",
            last_name="HBnB",
            email="admin@hbnb.io",
            password="Admin1234!",
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin créé !")
    else:
        print("ℹ️ Admin existe déjà")