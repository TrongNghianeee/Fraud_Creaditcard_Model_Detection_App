"""
Model routes - Fraud detection predictions using direct model
"""
from flask import request, jsonify, current_app
from app.blueprints.model import model_bp
from app.blueprints.model.fraud_detector import fraud_detector
import re


@model_bp.route('/predict-fraud', methods=['POST'])
def predict_fraud():
    """
    API mới: Predict fraud dựa trên 4 tham số (logic giống predict.py)
    
    Request body:
    {
        "amt": 500000,                    // Số tiền (VND)
        "gender": "Nam",                  // Giới tính (Nam/Nữ)
        "category": "xăng dầu",          // Loại giao dịch (Tiếng Việt)
        "transaction_time": "13:05:02"   // Thời gian giao dịch (HH:MM:SS)
    }
    
    Response:
    {
        "success": true,
        "prediction": {
            "is_fraud": false,
            "fraud_probability": 0.15,
            "safe_probability": 0.85,
            "risk_level": "low",
            "confidence": "high"
        },
        "input": {
            "amt_vnd": 500000,
            "amt_usd": 20.0,
            "gender": "Nam (M)",
            "category": "xăng dầu (gas_transport)",
            "transaction_time": "13:05:02 (hour: 13)"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['amt', 'gender', 'category', 'transaction_time']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        amt = data['amt']
        gender = data['gender']
        category = data['category']
        transaction_time = data['transaction_time']
        
        # Validate amt (Số tiền VND)
        try:
            amt = float(amt)
            if amt <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': f'Invalid amount: {amt}. Must be a positive number'
            }), 400
        
        # Validate gender (Giới tính: Nam/Nữ)
        if gender not in ['Nam', 'Nữ']:
            return jsonify({
                'success': False,
                'error': f'Invalid gender: {gender}. Must be "Nam" or "Nữ"'
            }), 400
        
        # Validate transaction_time (Thời gian: HH:MM:SS)
        time_pattern = r'^([0-1]?[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$'
        time_match = re.match(time_pattern, transaction_time)
        
        if not time_match:
            return jsonify({
                'success': False,
                'error': f'Invalid time format: {transaction_time}. Expected HH:MM:SS (e.g., 13:05:02)'
            }), 400
        
        current_app.logger.info(f"[PREDICT-FRAUD] Input: amt={amt} VND, gender={gender}, category={category}, time={transaction_time}")
        
        # Predict using fraud_detector (logic giống predict.py)
        result = fraud_detector.predict(
            amt=amt,
            gender=gender,
            category=category,
            transaction_time=transaction_time
        )
        
        # Determine risk level and confidence
        fraud_proba = result['fraud_probability']
        
        if fraud_proba < 0.1:
            risk_level = "very_low"
            confidence = "very_high"
        elif fraud_proba < 0.3:
            risk_level = "low"
            confidence = "high"
        elif fraud_proba < 0.5:
            risk_level = "medium"
            confidence = "medium"
        elif fraud_proba < 0.7:
            risk_level = "high"
            confidence = "medium"
        else:
            risk_level = "very_high"
            confidence = "high"
        
        converted = result['input_converted']
        
        current_app.logger.info(f"[PREDICT-FRAUD] Result: is_fraud={result['is_fraud']}, probability={fraud_proba:.2f}")
        
        return jsonify({
            'success': True,
            'prediction': {
                'is_fraud': result['is_fraud'],
                'fraud_probability': result['fraud_probability'],
                'safe_probability': result['safe_probability'],
                'risk_level': risk_level,
                'confidence': confidence
            },
            'input': {
                'amt_vnd': converted['amt_vnd'],
                'amt_usd': round(converted['amt_usd'], 2),
                'gender': f"{converted['gender_vn']} ({converted['gender_en']})",
                'category': f"{converted['category_vn']} ({converted['category_en']})",
                'transaction_time': f"{converted['transaction_time']} (hour: {converted['transaction_hour']})"
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"[PREDICT-FRAUD] Error: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Prediction failed: {str(e)}'
        }), 500
