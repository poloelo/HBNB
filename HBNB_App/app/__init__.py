from flask import Flask
from flask_restx import Api
from config import DevelopmentConfig
from app.extensions import bcrypt, jwt, db


def create_app(config_class=DevelopmentConfig):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialisation des extensions Flask
    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app)

    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API - Part 3',
        doc='/api/v1/',
        prefix='/api/v1'
    )

    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.users    import api as users_ns
    from app.api.v1.places   import api as places_ns
    from app.api.v1.reviews  import api as reviews_ns
    from app.api.v1.auth     import api as auth_ns

    api.add_namespace(amenities_ns, path='/amenities')
    api.add_namespace(users_ns,     path='/users')
    api.add_namespace(places_ns,    path='/places')
    api.add_namespace(reviews_ns,   path='/reviews')
    api.add_namespace(auth_ns,      path='/auth')

    # Création des tables SQLAlchemy au démarrage (si elles n'existent pas encore).
    # Les modèles User, Place, Review et Amenity sont mappés → leurs tables sont créées.
    with app.app_context():
        db.create_all()

    return app