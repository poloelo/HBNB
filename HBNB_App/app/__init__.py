from flask import Flask
from flask_restx import Api
from config import DevelopmentConfig


def create_app(config_class=DevelopmentConfig):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API - Part 2',
        doc='/api/v1/',
        prefix='/api/v1'
    )

    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.users    import api as users_ns
    from app.api.v1.places   import api as places_ns
    from app.api.v1.reviews  import api as reviews_ns

    api.add_namespace(amenities_ns, path='/amenities')
    api.add_namespace(users_ns,     path='/users')
    api.add_namespace(places_ns,    path='/places')
    api.add_namespace(reviews_ns,   path='/reviews')

    return app