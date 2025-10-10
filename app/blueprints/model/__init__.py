"""
Model Blueprint - API endpoints for ML model operations
"""
from flask import Blueprint

model_bp = Blueprint('model', __name__)

from app.blueprints.model import routes
