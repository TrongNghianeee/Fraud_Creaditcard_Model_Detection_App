"""
Configuration settings for the application
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # OpenAI Configuration (OpenRouter.ai)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL', 'https://openrouter.ai/api/v1')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'anthropic/claude-3.5-sonnet')
    
    # Exchange Rate
    USD_TO_VND_RATE = float(os.environ.get('USD_TO_VND_RATE', '24000'))
    
    # Model Configuration
    MODEL_PATH = os.environ.get('MODEL_PATH', 'models/fraud_detection_model.pkl')
    SCALER_PATH = os.environ.get('SCALER_PATH', 'models/scaler.pkl')
    
    # API Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max request size
    JSON_SORT_KEYS = False
    
    # CORS Configuration
    CORS_HEADERS = 'Content-Type'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
