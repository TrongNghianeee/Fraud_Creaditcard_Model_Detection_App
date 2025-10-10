"""
Application entry point
"""
import os
import sys
import signal
import atexit
import traceback
from app import create_app

# Create the Flask application
app = create_app()

ASCII_BANNER = """
============================================================
  Fraud Detection API Server
  Running on: http://{host}:{port}
  Debug Mode: {debug}
============================================================

Available API Endpoints:
------------------------------------------------------------
Health Check:
  GET  /health

Model APIs:
  POST /api/model/predict
  POST /api/model/predict-from-amount  * Fraud detection from amount
  POST /api/model/batch-predict
  GET  /api/model/model-info
  POST /api/model/reload

OpenAI APIs:
  POST /api/openai/parse-transaction
  POST /api/openai/analyze-transaction
  POST /api/openai/explain-prediction
  POST /api/openai/chat
  POST /api/openai/generate-report

Preprocess APIs (OCR + AI):
  POST /api/preprocess/extract-and-parse
  POST /api/preprocess/extract-text
  POST /api/preprocess/extract-text-batch
------------------------------------------------------------
"""

if __name__ == '__main__':
    try:
        # Get configuration from environment variables
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 5000))
        debug = os.environ.get('FLASK_DEBUG', '1') == '1'

        print(ASCII_BANNER.format(host=host, port=port, debug=debug))

        # Log when interpreter is exiting
        def _on_exit():
            print("\n[exit] Python interpreter exiting (atexit handler)")
        atexit.register(_on_exit)

        # Log when signals are received
        def _handle_signal(signum, frame):
            print(f"\n[signal] Received signal {signum}, shutting down server")
        # for sig in (signal.SIGINT, signal.SIGTERM, getattr(signal, 'SIGBREAK', signal.SIGINT)):
        #     try:
        #         signal.signal(sig, _handle_signal)
        #     except (ValueError, OSError, AttributeError):
        #         pass

        # Run with use_reloader=False to prevent auto-restart
        app.run(host=host, port=port, debug=debug, use_reloader=False)
        print("\n[info] app.run() returned (server stopped)")

    except KeyboardInterrupt:
        print("\n[info] Server stopped by user (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print("\n[error] FATAL ERROR: Server crashed!")
        print(f"Error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        sys.exit(1)
