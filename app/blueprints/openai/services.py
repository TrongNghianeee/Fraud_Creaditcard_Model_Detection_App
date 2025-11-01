"""
OpenAI services - Business logic for AI operations
"""
from openai import OpenAI
from flask import current_app
import json
import re


class OpenAIService:
    """Service class for OpenAI operations"""
    
    @classmethod
    def _get_client(cls):
        """Get OpenAI client with API key from config"""
        api_key = current_app.config.get('OPENAI_API_KEY')
        base_url = current_app.config.get('OPENAI_BASE_URL')
        
        if not api_key:
            raise ValueError("OpenAI API key not configured")
        
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        return client
    
    @classmethod
    def _get_completion(cls, messages, temperature=0.7, max_tokens=2000):
        """
        Get completion from OpenAI
        
        Args:
            messages (list): List of message dictionaries
            temperature (float): Response randomness (0-1)
            max_tokens (int): Maximum response length
            
        Returns:
            str: AI response
        """
        try:
            client = cls._get_client()
            model = current_app.config.get('OPENAI_MODEL', 'anthropic/claude-3.5-sonnet')
            
            current_app.logger.info(f"Calling AI model: {model}")
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            current_app.logger.error(f"AI API Error: {str(e)}")
            raise ValueError(f"AI service error: {str(e)}")
    
    @classmethod
    def parse_transaction_text(cls, ocr_text):
        """
        Parse OCR text and extract transaction information using AI
        
        Args:
            ocr_text (str): Raw OCR text from transaction image
            
        Returns:
            dict: Parsed transaction information (4 fields cho fraud prediction)
        """
        
        system_prompt = """Bạn là một AI chuyên phân tích giao dịch ngân hàng từ văn bản OCR.
Nhiệm vụ của bạn là trích xuất thông tin giao dịch từ văn bản và trả về JSON với format chính xác.

QUY TẮC QUAN TRỌNG:
- CHỈ TRẢ VỀ JSON, KHÔNG THÊM BẤT KỲ TEXT NÀO KHÁC
- KHÔNG THÊM MARKDOWN (```json hoặc ```)
- KHÔNG THÊM GIẢI THÍCH, CHÚ THÍCH HAY COMMENT
- CHỈ TRẢ VỀ 1 OBJECT JSON DUY NHẤT

QUAN TRỌNG - Chỉ trích xuất 4 thông tin sau:
1. amt (số tiền VND) - Bắt buộc phải là số nguyên, không dấu phẩy/chấm
2. gender (giới tính) - Chỉ "Nam" hoặc "Nữ", phải viết hoa chữ cái đầu
3. category (loại giao dịch) - Dựa vào nội dung để xếp loại
4. transaction_time (thời gian giao dịch) - Format HH:MM:SS (ví dụ: 13:05:02)

DANH SÁCH CATEGORY hợp lệ (chọn 1 trong các loại sau):
- 'giải trí': Xem phim, karaoke, game, giải trí
- 'ăn uống': Nhà hàng, quán ăn, cafe, đồ ăn thức uống
- 'xăng dầu': Xăng, dầu, nhiên liệu, cửa hàng xăng
- 'siêu thị online': Mua sắm online tại siêu thị, grocery online
- 'siêu thị': Siêu thị, cửa hàng tiện lợi, grocery
- 'sức khỏe': Y tế, thuốc, bệnh viện, phòng khám, gym, fitness
- 'nội thất': Đồ nội thất, trang trí nhà cửa
- 'trẻ em': Đồ chơi trẻ em, sữa, tã, đồ dùng trẻ em, pet
- 'khác online': Mua sắm online không rõ ràng
- 'khác': Giao dịch không xác định hoặc không thuộc loại nào
- 'chăm sóc cá nhân': Spa, làm đẹp, mỹ phẩm, salon
- 'mua sắm online': Mua sắm online quần áo, phụ kiện
- 'mua sắm': Mua sắm trực tiếp quần áo, giày dép, phụ kiện
- 'du lịch': Khách sạn, vé máy bay, tour du lịch

LƯU Ý:
- Nếu không tìm thấy thông tin gender, mặc định là null
- Nếu không xác định được category, mặc định là 'khác'
- Số tiền (amt) phải là số nguyên VND, không có dấu
- Thời gian (transaction_time) phải theo format HH:MM:SS (giờ:phút:giây)
- TUYỆT ĐỐI CHỈ TRẢ VỀ JSON, KHÔNG TEXT THỪA"""

        user_prompt = f"""Phân tích văn bản giao dịch sau và trích xuất 4 thông tin:

{ocr_text}

QUAN TRỌNG: Trả về JSON với CẤU TRÚC CHÍNH XÁC SAU (KHÔNG thay đổi tên key):
{{
  "amt": <số tiền VND - số nguyên, VD: 500000>,
  "gender": "<Nam hoặc Nữ hoặc null>",
  "category": "<loại giao dịch>",
  "transaction_time": "<HH:MM:SS - VD: 13:05:02>"
}}

VÍ DỤ OUTPUT ĐÚNG:
{{
  "amt": 500000,
  "gender": "Nam",
  "category": "xăng dầu",
  "transaction_time": "13:05:02"
}}

TUYỆT ĐỐI KHÔNG DÙNG:
- "transaction_hour" (SAI - không được phép)
- "time" (SAI)
- "hour" (SAI)

CHỈ DÙNG KEY: "transaction_time" với format "HH:MM:SS"

CHÚ Ý:
- amt PHẢI là số nguyên VND (ví dụ: 500000, không phải "500,000" hay "500.000")
- gender CHỈ có thể là "Nam", "Nữ" hoặc null
- category PHẢI chọn từ danh sách category hợp lệ ở trên
- transaction_time PHẢI có key chính xác là "transaction_time" và format "HH:MM:SS" (ví dụ: "13:05:02", "09:30:15")"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            current_app.logger.info(f"Starting AI parsing for OCR text (length: {len(ocr_text)} chars)")
            
            response = cls._get_completion(messages, temperature=0.1, max_tokens=500)
            
            current_app.logger.info(f"AI Response received (length: {len(response)} chars)")
            current_app.logger.info(f"AI Response preview: {response[:300]}...")
            
            # Clean response - remove markdown code blocks and extra text
            response = response.strip()
            
            # Remove markdown code blocks
            if response.startswith('```'):
                response = re.sub(r'^```(?:json)?\s*\n', '', response)
                response = re.sub(r'\n```\s*$', '', response)
            
            # Extract JSON from text if there's extra content
            # Try to find JSON object pattern
            import re
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
                current_app.logger.info(f"Extracted JSON from response: {response[:200]}...")
            
            # Parse JSON
            parsed_data = json.loads(response)
            
            # FIX: Nếu AI trả về "transaction_hour" thay vì "transaction_time", convert ngay
            if 'transaction_hour' in parsed_data and 'transaction_time' not in parsed_data:
                hour = parsed_data.pop('transaction_hour')
                # Convert hour number to HH:MM:SS format (assume 00:00 for minutes/seconds)
                if isinstance(hour, (int, float)):
                    parsed_data['transaction_time'] = f"{int(hour):02d}:00:00"
                    current_app.logger.warning(f"AI returned 'transaction_hour'={hour}, converted to transaction_time={parsed_data['transaction_time']}")
                else:
                    parsed_data['transaction_time'] = None
                    current_app.logger.warning(f"AI returned invalid 'transaction_hour'={hour}, setting transaction_time to null")
            
            # Validate required fields
            required_fields = ['amt', 'gender', 'category', 'transaction_time']
            
            for field in required_fields:
                if field not in parsed_data:
                    parsed_data[field] = None
            
            # Additional validation
            valid_categories = [
                'giải trí', 'ăn uống', 'xăng dầu', 'siêu thị online', 'siêu thị',
                'sức khỏe', 'nội thất', 'trẻ em', 'khác online', 'khác',
                'chăm sóc cá nhân', 'mua sắm online', 'mua sắm', 'du lịch'
            ]
            
            # Ensure category is valid, default to 'khác' if not
            if parsed_data.get('category') not in valid_categories:
                current_app.logger.warning(f"Invalid category '{parsed_data.get('category')}', defaulting to 'khác'")
                parsed_data['category'] = 'khác'
            
            # Ensure gender is valid
            if parsed_data.get('gender') and parsed_data['gender'] not in ['Nam', 'Nữ']:
                current_app.logger.warning(f"Invalid gender '{parsed_data.get('gender')}', setting to null")
                parsed_data['gender'] = None
            
            # Validate transaction_time format (HH:MM:SS)
            if parsed_data.get('transaction_time'):
                import re
                time_pattern = r'^([0-1]?[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])$'
                if not re.match(time_pattern, str(parsed_data['transaction_time'])):
                    current_app.logger.warning(f"Invalid time format '{parsed_data.get('transaction_time')}', setting to null")
                    parsed_data['transaction_time'] = None
            
            # Ensure amt is a number
            if parsed_data.get('amt') is not None:
                try:
                    parsed_data['amt'] = int(parsed_data['amt'])
                except (ValueError, TypeError):
                    current_app.logger.warning(f"Invalid amount '{parsed_data.get('amt')}', setting to null")
                    parsed_data['amt'] = None
            
            current_app.logger.info("AI parsing successful!")
            return {
                'success': True,
                'data': parsed_data,
                'raw_text': ocr_text
            }
            
        except ValueError as e:
            error_msg = str(e)
            current_app.logger.error(f"AI API Error: {error_msg}")
            return {
                'success': False,
                'error': f'AI API error: {error_msg}'
            }
        except json.JSONDecodeError as e:
            current_app.logger.error(f"JSON Parse Error: {str(e)}")
            current_app.logger.error(f"AI Response was: {response if 'response' in locals() else 'N/A'}")
            return {
                'success': False,
                'error': f'AI trả về JSON không hợp lệ. Chi tiết: {str(e)}',
                'raw_response': response if 'response' in locals() else None
            }
        except Exception as e:
            current_app.logger.error(f"AI Parsing Exception: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': f'Lỗi không xác định: {str(e) if str(e) else "Unknown error"}'
            }
    
    @classmethod
    def analyze_fraud_risk(cls, transaction_text, transaction_data=None):
        """
        Analyze fraud risk using AI
        
        Args:
            transaction_text (str): Description of the transaction
            transaction_data (dict): Additional transaction data
            
        Returns:
            dict: Analysis result with risk assessment
        """
        prompt = f"""Analyze the following transaction for potential fraud risk:

Transaction Description: {transaction_text}
"""
        
        if transaction_data:
            prompt += f"\nTransaction Data: {transaction_data}"
        
        prompt += """

Please provide:
1. Risk Level (Low/Medium/High)
2. Risk Factors identified
3. Recommendations

Format your response as a structured analysis."""
        
        messages = [
            {
                "role": "system",
                "content": "You are a fraud detection expert analyzing credit card transactions."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        analysis = cls._get_completion(messages, temperature=0.3)
        
        return {
            'analysis': analysis,
            'transaction_text': transaction_text
        }
    
    @classmethod
    def explain_prediction(cls, prediction_result, transaction_data):
        """
        Generate human-readable explanation for a model prediction
        
        Args:
            prediction_result (dict): Model prediction output
            transaction_data (dict): Transaction details
            
        Returns:
            str: Natural language explanation
        """
        is_fraud = prediction_result.get('is_fraud', False)
        probability = prediction_result.get('fraud_probability', 0)
        
        prompt = f"""Explain the following fraud detection result to a non-technical user:

Prediction: {'Fraudulent' if is_fraud else 'Legitimate'}
Fraud Probability: {probability:.2%}
Transaction Data: {transaction_data}

Provide a clear, concise explanation of why this transaction was flagged or cleared, 
highlighting the key factors that influenced the decision."""
        
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant explaining fraud detection results in simple terms."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        return cls._get_completion(messages, temperature=0.5)
    
    @classmethod
    def chat(cls, message, context=None):
        """
        Handle general chat about fraud detection
        
        Args:
            message (str): User message
            context (dict): Additional context
            
        Returns:
            str: AI response
        """
        system_message = """You are an AI assistant specializing in credit card fraud detection. 
You help users understand fraud patterns, prevention strategies, and transaction analysis."""
        
        user_message = message
        if context:
            user_message = f"Context: {context}\n\nQuestion: {message}"
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        return cls._get_completion(messages, temperature=0.7)
    
    @classmethod
    def generate_fraud_report(cls, transactions, time_period):
        """
        Generate a comprehensive fraud analysis report
        
        Args:
            transactions (list): List of transactions to analyze
            time_period (str): Time period description
            
        Returns:
            str: Generated report
        """
        prompt = f"""Generate a fraud analysis report for {time_period}.

Number of Transactions: {len(transactions)}

Analyze the transactions and provide:
1. Executive Summary
2. Fraud Statistics
3. Common Patterns Detected
4. Risk Areas
5. Recommendations

Keep the report professional and actionable."""
        
        messages = [
            {
                "role": "system",
                "content": "You are a fraud analyst generating reports for stakeholders."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        return cls._get_completion(messages, temperature=0.4, max_tokens=1000)
