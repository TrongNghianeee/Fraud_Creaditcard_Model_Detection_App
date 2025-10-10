"""
Model routes - Handle ML model related operations
"""
from flask import request, jsonify, current_app
from app.blueprints.model import model_bp
from app.blueprints.model.services import ModelService


@model_bp.route('/reload', methods=['POST'])
def reload_model():
    """Reload the ML model (useful after model updates)"""
    try:
        ModelService.reload_model()
        return jsonify({
            'message': 'Model reloaded successfully'
        }), 200
    except Exception as e:
        current_app.logger.error(f"Model reload error: {str(e)}")
        return jsonify({'error': 'Failed to reload model'}), 500


@model_bp.route('/predict-from-amount', methods=['POST'])
def predict_from_amount():
    """
    Predict fraud based on transaction amount from OCR
    
    This endpoint finds a matching transaction in the test dataset based on amount
    and uses it to predict fraud probability.
    
    Request body:
    {
        "amount_usd": 20.50,
        "amount_vnd": 500000  (optional)
    }
    
    Response:
    {
        "success": true,
        "amount_usd": 20.50,
        "matched_transaction": {...},
        "prediction": {
            "is_fraud": false,
            "fraud_probability": 0.05,
            "confidence": "high",
            "risk_level": "low"
        },
        "features_used": [...],
        "model_version": "v2_flexible"
    }
    """
    result = None
    try:
        current_app.logger.info("=== START predict-from-amount ===")
        data = request.get_json()
        current_app.logger.info(f"Request data: {data}")
        
        if not data or 'amount_usd' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing amount_usd in request body'
            }), 400
        
        amount_usd = float(data['amount_usd'])
        
        if amount_usd < 0:
            return jsonify({
                'success': False,
                'error': 'amount_usd must be non-negative'
            }), 400
        
        current_app.logger.info(f"Calling ModelService.predict_from_amount({amount_usd})")
        
        # Use ModelService to predict from amount
        result = ModelService.predict_from_amount(amount_usd)
        
        current_app.logger.info("=" * 80)
        current_app.logger.info("[ROUTE] BACK FROM ModelService.predict_from_amount()")
        current_app.logger.info(f"[ROUTE] Result received: type={type(result)}, keys={list(result.keys()) if isinstance(result, dict) else 'NOT A DICT'}")
        current_app.logger.info("=" * 80)
        
        current_app.logger.info("ModelService.predict_from_amount completed successfully")
        current_app.logger.info(f"Result type: {type(result)}")
        
        current_app.logger.info("[ROUTE] ABOUT TO CALL jsonify()")
        response = jsonify(result)
        current_app.logger.info("[ROUTE] jsonify() COMPLETED")
        
        current_app.logger.info("=" * 80)
        current_app.logger.info("[ROUTE] ABOUT TO RETURN RESPONSE WITH STATUS 200")
        current_app.logger.info("=" * 80)
        
        return response, 200
        
    except ValueError as e:
        current_app.logger.error(f"ValueError in predict-from-amount: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Invalid input: {str(e)}'
        }), 400
    except FileNotFoundError as e:
        current_app.logger.error(f"FileNotFoundError in predict-from-amount: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Required file not found: {str(e)}'
        }), 500
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        current_app.logger.error(f"Exception in predict-from-amount: {str(e)}\n{error_trace}")
        return jsonify({
            'success': False,
            'error': f'An error occurred during prediction: {str(e)}'
        }), 500
    finally:
        current_app.logger.info("=== FINALLY block in predict-from-amount ===")
        if result:
            current_app.logger.info(f"Result keys: {result.keys() if isinstance(result, dict) else 'NOT A DICT'}")
