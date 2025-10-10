"""
Preprocess Blueprint - API endpoints for data preprocessing
"""
from flask import Blueprint

preprocess_bp = Blueprint('preprocess', __name__)

from app.blueprints.preprocess import routes
