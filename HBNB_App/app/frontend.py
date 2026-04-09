"""Blueprint to serve the static frontend from part4/"""

import os
from flask import Blueprint, send_from_directory

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'part4')
FRONTEND_DIR = os.path.abspath(FRONTEND_DIR)

frontend_bp = Blueprint('frontend', __name__)


@frontend_bp.route('/')
@frontend_bp.route('/index.html')
def index():
    return send_from_directory(FRONTEND_DIR, 'index.html')


@frontend_bp.route('/login.html')
def login():
    return send_from_directory(FRONTEND_DIR, 'login.html')


@frontend_bp.route('/place.html')
def place():
    return send_from_directory(FRONTEND_DIR, 'place.html')


@frontend_bp.route('/add_review.html')
def add_review():
    return send_from_directory(FRONTEND_DIR, 'add_review.html')


@frontend_bp.route('/signup.html')
def signup():
    return send_from_directory(FRONTEND_DIR, 'signup.html')


@frontend_bp.route('/profile.html')
def profile():
    return send_from_directory(FRONTEND_DIR, 'profile.html')


@frontend_bp.route('/create_place.html')
def create_place():
    return send_from_directory(FRONTEND_DIR, 'create_place.html')


@frontend_bp.route('/scripts.js')
def scripts():
    return send_from_directory(FRONTEND_DIR, 'scripts.js')


@frontend_bp.route('/styles/<path:filename>')
def styles(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'styles'), filename)


@frontend_bp.route('/images/<path:filename>')
def images(filename):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'images'), filename)
