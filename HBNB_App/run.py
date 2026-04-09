#!/usr/bin/env python3

"""Application entry point"""
import os
from flask import send_from_directory
from app import create_app
from flask_cors import CORS

app = create_app()
CORS(app)

PART4_DIR = os.path.join(os.path.dirname(__file__), 'part4')


@app.route('/')
def frontend_index():
    """Serve the main page."""
    return send_from_directory(PART4_DIR, 'index.html')


@app.route('/<path:filename>')
def frontend_static(filename):
    """Serve static frontend files from the part4/ directory."""
    return send_from_directory(PART4_DIR, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
