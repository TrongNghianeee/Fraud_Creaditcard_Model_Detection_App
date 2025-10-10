"""
OpenAI Blueprint - API endpoints for OpenAI integration
"""
from flask import Blueprint

openai_bp = Blueprint('openai', __name__)

from app.blueprints.openai import routes
