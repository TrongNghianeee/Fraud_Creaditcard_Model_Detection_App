"""
Application Factory Pattern
"""
from flask import Flask, send_from_directory, request
from flask_cors import CORS
from app.config import Config
import os


def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__, static_folder='../static')
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    from app.blueprints.model import model_bp
    from app.blueprints.openai import openai_bp
    from app.blueprints.preprocess import preprocess_bp
    
    app.register_blueprint(model_bp, url_prefix='/api/model')
    app.register_blueprint(openai_bp, url_prefix='/api/openai')
    app.register_blueprint(preprocess_bp, url_prefix='/api/preprocess')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register after_request handler to catch post-response errors
    @app.after_request
    def after_request_logging(response):
        """Log after each request"""
        try:
            app.logger.info(f"After request: {request.method} {request.path} -> {response.status_code}")
            app.logger.info("Response successfully prepared, about to return to client")
            return response
        except Exception as e:
            app.logger.error(f"ERROR IN after_request: {e}")
            import traceback
            app.logger.error(traceback.format_exc())
            raise
    
    # Register teardown handler to catch cleanup errors
    @app.teardown_request
    def teardown_request_logging(exception=None):
        """Log request teardown"""
        try:
            if exception:
                app.logger.error(f"TEARDOWN with exception: {exception}")
                import traceback
                app.logger.error(traceback.format_exc())
            else:
                app.logger.info("TEARDOWN: Request completed successfully")
        except Exception as e:
            app.logger.error(f"ERROR IN teardown_request: {e}")
            import traceback
            app.logger.error(traceback.format_exc())
    
    @app.route('/')
    def index():
        """Serve the HTML test page"""
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/health')
    def health_check():
        return {'status': 'ok', 'message': 'Fraud Detection API is running'}, 200
    
    return app


def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {error}")
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request'}, 400
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Catch all unhandled exceptions"""
        import traceback
        error_trace = traceback.format_exc()
        app.logger.error(f"Unhandled exception: {error}\n{error_trace}")
        return {'error': f'Unhandled error: {str(error)}'}, 500
