"""
OpenAI routes - Handle AI-powered analysis and insights
"""
from flask import request, jsonify, current_app
from app.blueprints.openai import openai_bp
from app.blueprints.openai.services import OpenAIService


@openai_bp.route('/parse-transaction', methods=['POST'])
def parse_transaction():
    """
    Parse transaction text using AI to extract structured information
    
    Request body:
    {
        "text": "OCR text from transaction image"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "sender_name": "NGUYEN VAN A",
            "receiver_name": "TRAN THI B",
            "amount_vnd": 500000,
            "amount_usd": 20.83,
            "time": "15:05:02",
            "time_in_seconds": 54302,
            "date": "09/09/2025",
            "transaction_content": "Chuyen tien tra coc",
            "sender_bank": "AGRIBANK",
            "receiver_bank": "VPBank",
            "transaction_id": "599022",
            "transaction_fee": "Miễn phí"
        },
        "raw_text": "Original OCR text..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing text in request body'
            }), 400
        
        text = data['text']
        
        if not text or len(text.strip()) == 0:
            return jsonify({
                'success': False,
                'error': 'Text cannot be empty'
            }), 400
        
        # Parse transaction using AI
        result = OpenAIService.parse_transaction_text(text)
        
        if result.get('success'):
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except ValueError as e:
        current_app.logger.error(f"Transaction parsing validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Transaction parsing error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred during transaction parsing'
        }), 500
