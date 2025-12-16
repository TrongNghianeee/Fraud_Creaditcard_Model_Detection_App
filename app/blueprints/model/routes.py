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
    API: Predict fraud với 15 features (FA-selected) - theo logic predict.py
    
    Request body (7 trường BẮT BUỘC + 1 optional):
    {
        "amt": 500000,                    // Số tiền (VND) [REQUIRED]
        "gender": "Nam",                  // Giới tính (Nam/Nữ) [REQUIRED]
        "category": "xăng dầu",          // Loại giao dịch (Tiếng Việt) [REQUIRED]
        "transaction_hour": 13,           // Giờ giao dịch (0-23) [REQUIRED]
        "transaction_day": 5,             // Ngày trong tuần (0-6, Mon=0) [REQUIRED]
        "age": 28,                        // Tuổi (18-100) [REQUIRED]
        "city": "ha noi",                 // Thành phố/Tỉnh VN [REQUIRED]
        "city_pop": 8054000,              // Dân số tỉnh/thành [REQUIRED - app tự lookup]
        "transaction_month": 6            // Tháng (1-12) [OPTIONAL, default=6]
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
            "transaction_hour": 13,
            "transaction_day": 5,
            "age": 28,
            "city": "ha noi",
            "city_pop": 8054000
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
        
        # Validate required fields (7 trường bắt buộc, city_pop là OPTIONAL)
        required_fields = ['amt', 'gender', 'category', 'transaction_hour', 
                          'transaction_day', 'age', 'city']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        amt = data['amt']
        gender = data['gender']
        category = data['category']
        transaction_hour = data['transaction_hour']
        transaction_day = data['transaction_day']
        age = data['age']
        city = data['city']
        city_pop = data.get('city_pop')  # OPTIONAL - nếu app gửi thì dùng, không thì backend tự lookup
        transaction_month = data.get('transaction_month')  # Optional
        
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
        
        # Validate transaction_hour (0-23)
        try:
            transaction_hour = int(transaction_hour)
            if not (0 <= transaction_hour <= 23):
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': f'Invalid transaction_hour: {transaction_hour}. Must be 0-23'
            }), 400
        
        # Validate transaction_day (0-6, Monday=0, Sunday=6)
        try:
            transaction_day = int(transaction_day)
            if not (0 <= transaction_day <= 6):
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': f'Invalid transaction_day: {transaction_day}. Must be 0-6 (Monday=0, Sunday=6)'
            }), 400
        
        # Validate age (18-100)
        try:
            age = int(age)
            if not (18 <= age <= 100):
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': f'Invalid age: {age}. Must be 18-100'
            }), 400
        
        # Validate city_pop nếu có (nếu không có, fraud_detector sẽ tự lookup)
        if city_pop is not None:
            try:
                city_pop = int(city_pop)
                if city_pop <= 0:
                    raise ValueError("City population must be positive")
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': f'Invalid city_pop: {city_pop}. Must be a positive integer'
                }), 400
        
        # Validate transaction_month if provided
        if transaction_month is not None:
            try:
                transaction_month = int(transaction_month)
                if not (1 <= transaction_month <= 12):
                    raise ValueError()
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'error': f'Invalid transaction_month: {transaction_month}. Must be 1-12'
                }), 400
        
        current_app.logger.info(
            f"[PREDICT-FRAUD] Input: amt={amt} VND, gender={gender}, category={category}, "
            f"hour={transaction_hour}, day={transaction_day}, age={age}, city={city}, city_pop={city_pop}"
        )
        
        # Predict using fraud_detector (với 7 required + city_pop + 1 optional fields)
        result = fraud_detector.predict(
            amt=amt,
            gender=gender,
            category=category,
            transaction_hour=transaction_hour,
            transaction_day=transaction_day,
            age=age,
            city=city,
            city_pop=city_pop,  # App đã lookup, truyền trực tiếp
            transaction_month=transaction_month
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
                'transaction_hour': converted['transaction_hour'],
                'transaction_day': converted['transaction_day'],
                'transaction_month': converted['transaction_month'],
                'age': converted['age'],
                'city': converted['city'],
                'city_pop': converted['city_pop']  # Return as integer, not formatted string
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
