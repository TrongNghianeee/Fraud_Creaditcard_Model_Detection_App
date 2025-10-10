"""
Preprocess routes - Handle OCR text extraction from images
"""
from flask import request, jsonify, current_app
from app.blueprints.preprocess import preprocess_bp
from app.blueprints.preprocess.services import OCRService
from app.blueprints.openai.services import OpenAIService
import base64


@preprocess_bp.route('/extract-and-parse', methods=['POST'])
def extract_and_parse():
    """
    Extract text from image using OCR and parse with AI in one step
    
    Request body (form-data):
    - file: image file (jpg, png, jpeg, etc.)
    - language: "vie+eng" (optional)
    
    Response:
    {
        "success": true,
        "transaction": {
            "sender_name": "NGUYEN VAN A",
            "receiver_name": "TRAN THI B",
            "amount_vnd": 500000,
            "amount_usd": 20.83,
            ...
        },
        "ocr_confidence": 85.5,
        "processing_time": 2.5
    }
    """
    try:
        from app.blueprints.openai.services import OpenAIService
        import time
        
        start_time = time.time()
        language = request.form.get('language', 'vie+eng')
        
        # Check if image is sent as file upload
        if 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected'
                }), 400
            
            # Check file extension
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
            file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            
            if file_ext not in allowed_extensions:
                return jsonify({
                    'success': False,
                    'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
                }), 400
            
            # Read file content
            image_data = file.read()
            
        # Check if image is sent as base64
        elif request.is_json and 'image' in request.json:
            import base64
            image_base64 = request.json['image']
            
            # Remove data URL prefix if present
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            try:
                image_data = base64.b64decode(image_base64)
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': 'Invalid base64 image data'
                }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'No image provided. Send "file" in form-data or "image" (base64) in JSON body'
            }), 400
        
        # Step 1: Extract text using OCR
        ocr_result = OCRService.extract_text_from_image(image_data, language)
        
        if not ocr_result.get('success'):
            return jsonify({
                'success': False,
                'error': 'OCR extraction failed'
            }), 400
        
        extracted_text = ocr_result.get('text', '')
        ocr_confidence = ocr_result.get('confidence', 0)
        
        if not extracted_text or len(extracted_text.strip()) == 0:
            return jsonify({
                'success': False,
                'error': 'No text extracted from image'
            }), 400
        
        # Step 2: Parse transaction with AI
        parse_result = OpenAIService.parse_transaction_text(extracted_text)
        
        total_time = time.time() - start_time
        
        # Always return success for OCR, but flag if AI parsing failed
        if not parse_result.get('success'):
            return jsonify({
                'success': True,  # OCR succeeded
                'ai_parsing_success': False,  # But AI parsing failed
                'ai_error': parse_result.get('error', 'AI parsing failed'),
                'ocr_text': extracted_text,
                'ocr_confidence': ocr_confidence,
                'processing_time': round(total_time, 2),
                'language': language
            }), 200
        
        # Both OCR and AI parsing succeeded
        return jsonify({
            'success': True,
            'ai_parsing_success': True,
            'transaction': parse_result.get('data'),
            'ocr_confidence': ocr_confidence,
            'processing_time': round(total_time, 2),
            'language': language
        }), 200
        
    except ValueError as e:
        current_app.logger.error(f"Extract and parse validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Extract and parse error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred during processing'
        }), 500


@preprocess_bp.route('/extract-text', methods=['POST'])
def extract_text():
    """
    Extract text from image using OCR only (without AI parsing)
    
    Request body (form-data):
    - file: image file (jpg, png, jpeg, etc.)
    - language: "vie+eng" (optional, default: "vie+eng")
    
    OR send JSON with base64:
    {
        "image": "base64_encoded_image_string",
        "language": "vie+eng" (optional)
    }
    
    Response:
    {
        "success": true,
        "text": "Extracted text from image",
        "confidence": 85.5,
        "language": "vie+eng",
        "processing_time": 1.23,
        "word_count": 50,
        "char_count": 250
    }
    """
    try:
        language = request.form.get('language') or request.json.get('language', 'vie+eng') if request.is_json else 'vie+eng'
        
        # Check if image is sent as file upload
        if 'file' in request.files:
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'error': 'No file selected'
                }), 400
            
            # Check file extension
            allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
            file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            
            if file_ext not in allowed_extensions:
                return jsonify({
                    'success': False,
                    'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
                }), 400
            
            # Read file content
            image_data = file.read()
            
        # Check if image is sent as base64
        elif request.is_json and 'image' in request.json:
            image_base64 = request.json['image']
            
            # Remove data URL prefix if present
            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            try:
                image_data = base64.b64decode(image_base64)
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': 'Invalid base64 image data'
                }), 400
        else:
            return jsonify({
                'success': False,
                'error': 'No image provided. Send "file" in form-data or "image" (base64) in JSON body'
            }), 400
        
        # Extract text using OCR
        result = OCRService.extract_text_from_image(image_data, language)
        
        return jsonify(result), 200
        
    except ValueError as e:
        current_app.logger.error(f"OCR validation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"OCR extraction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An error occurred during text extraction'
        }), 500
