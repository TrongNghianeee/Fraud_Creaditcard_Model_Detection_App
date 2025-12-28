"""
Model routes - Fraud detection predictions using direct model
"""
from flask import request, jsonify, current_app
from app.blueprints.model import model_bp
from app.blueprints.model.fraud_detector import fraud_detector
from app.blueprints.openai.services import OpenAIService
import re
import time
import json
import hashlib
import threading


# Simple in-memory caches (per-process) to avoid recomputing explanations for identical inputs.
# NOTE: In multi-worker deployments (gunicorn/uwsgi), each worker has its own cache.
_cache_lock = threading.Lock()
_CONTRIB_CACHE = {}  # key -> (ts, factors)
_AI_EXPL_CACHE = {}  # key -> (ts, explanation)

_CACHE_TTL_SECONDS = 10 * 60  # 10 minutes
_CACHE_MAX_ITEMS = 256


def _cache_key_from_obj(obj) -> str:
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _cache_get(cache: dict, key: str):
    now = time.time()
    with _cache_lock:
        item = cache.get(key)
        if not item:
            return None
        ts, value = item
        if now - ts > _CACHE_TTL_SECONDS:
            cache.pop(key, None)
            return None
        return value


def _cache_set(cache: dict, key: str, value):
    now = time.time()
    with _cache_lock:
        cache[key] = (now, value)
        if len(cache) > _CACHE_MAX_ITEMS:
            # Evict oldest entries
            oldest = sorted(cache.items(), key=lambda kv: kv[1][0])[: max(1, len(cache) - _CACHE_MAX_ITEMS)]
            for k, _ in oldest:
                cache.pop(k, None)


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
        explanation_detail = data.get('explanation_detail', 'full')  # Optional: short|full
        
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
        
        response_payload = {
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
        }

        # Only call AI explanation when fraud=true
        if result.get('is_fraud') is True:
            try:
                # Cache key based on normalized request inputs (not on derived fields)
                contrib_key = _cache_key_from_obj({
                    'amt': float(amt),
                    'gender': gender,
                    'category': category,
                    'transaction_hour': int(transaction_hour),
                    'transaction_day': int(transaction_day),
                    'age': int(age),
                    'city': city,
                    'city_pop': int(city_pop) if city_pop is not None else None,
                    'transaction_month': int(transaction_month) if transaction_month is not None else None,
                })

                factors_for_ai = _cache_get(_CONTRIB_CACHE, contrib_key)
                if factors_for_ai is None:
                    # Compute model-level contribution factors (no external AI) to ground the explanation
                    model_explain = fraud_detector.explain_contributions(
                        amt=amt,
                        gender=gender,
                        category=category,
                        transaction_hour=transaction_hour,
                        transaction_day=transaction_day,
                        age=age,
                        city=city,
                        city_pop=city_pop,
                        transaction_month=transaction_month,
                        top_k=6
                    )

                    all_factors = model_explain.get('top_factors', []) or []
                    user_factors = [f for f in all_factors if f.get('source') == 'user_input']
                    factors_for_ai = user_factors if user_factors else all_factors
                    _cache_set(_CONTRIB_CACHE, contrib_key, factors_for_ai)

                # Cache AI explanation as it is typically the slowest step
                ai_key = _cache_key_from_obj({
                    'prediction': {
                        'is_fraud': True,
                        # rounding makes cache more stable while keeping meaning
                        'fraud_probability': round(float(response_payload['prediction']['fraud_probability']), 6),
                        'risk_level': response_payload['prediction']['risk_level'],
                    },
                    'input': response_payload['input'],
                    'model_top_factors': factors_for_ai,
                })

                explanation = _cache_get(_AI_EXPL_CACHE, ai_key)
                if explanation is None:
                    explanation = OpenAIService.explain_prediction(
                        prediction_result=response_payload['prediction'],
                        transaction_data={
                            **response_payload['input'],
                            # Grounding evidence from the model
                            'model_top_factors': factors_for_ai
                        },
                        explanation_detail=explanation_detail
                    )
                    _cache_set(_AI_EXPL_CACHE, ai_key, explanation)
                response_payload['ai_explanation'] = explanation
                response_payload['ai_explanation_success'] = True
                # Optional: return factors for debugging/inspection (clients can ignore)
                response_payload['model_top_factors'] = factors_for_ai
            except Exception as ai_err:
                current_app.logger.error(f"[PREDICT-FRAUD] AI explanation error: {str(ai_err)}")
                response_payload['ai_explanation'] = None
                response_payload['ai_explanation_success'] = False
                response_payload['ai_explanation_error'] = str(ai_err)

        return jsonify(response_payload), 200
        
    except Exception as e:
        current_app.logger.error(f"[PREDICT-FRAUD] Error: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Prediction failed: {str(e)}'
        }), 500
