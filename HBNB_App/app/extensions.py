"""
Extensions Flask partagées.

Instanciées ici sans app, puis liées à l'app via init_app()
dans la factory create_app(). Ce pattern évite les imports circulaires.
"""

from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

bcrypt = Bcrypt()
jwt = JWTManager()
