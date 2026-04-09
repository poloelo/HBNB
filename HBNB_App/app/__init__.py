from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from config import DevelopmentConfig
from app.extensions import bcrypt, jwt, db

def create_app(config_class=DevelopmentConfig):
    """Application factory pattern"""
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
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

    with app.app_context():
        db.create_all()
        from app.models.user import User
        if not User.query.filter_by(email="admin@hbnb.io").first():
            admin = User(
                first_name="Admin",
                last_name="HBnB",
                email="admin@hbnb.io",
                password="Admin1234!",
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()

    return app