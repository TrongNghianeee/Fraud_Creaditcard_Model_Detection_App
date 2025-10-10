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
            dict: Parsed transaction information
        """
        usd_rate = current_app.config.get('USD_TO_VND_RATE', 24000)
        
        system_prompt = """Bạn là một AI chuyên phân tích giao dịch ngân hàng từ văn bản OCR.
Nhiệm vụ của bạn là trích xuất thông tin giao dịch từ văn bản và trả về JSON với format chính xác.

Lưu ý:
- Nếu không tìm thấy thông tin, để giá trị là null
- Số tiền phải là số, không có dấu phẩy hoặc dấu chấm (ví dụ: 500000 thay vì 500,000)
- Thời gian phải theo format đúng
- Tên người phải viết hoa đúng cách
- MGD (Mã giao dịch) thường là số hoặc mã định danh
"""

        user_prompt = f"""Phân tích văn bản giao dịch sau và trích xuất thông tin:

{ocr_text}

Trả về JSON với cấu trúc sau (KHÔNG thêm markdown, chỉ trả JSON thuần):
{{
  "sender_name": "Họ tên người gửi (viết hoa đúng)",
  "receiver_name": "Họ tên người nhận (viết hoa đúng)",
  "amount_vnd": số tiền VND (số nguyên, không dấu),
  "amount_usd": số tiền USD (làm tròn 2 chữ số thập phân),
  "time": "HH:MM:SS",
  "time_in_seconds": tổng số giây từ 00:00:00,
  "date": "DD/MM/YYYY",
  "transaction_content": "Nội dung chuyển khoản",
  "sender_bank": "Ngân hàng gửi",
  "receiver_bank": "Ngân hàng nhận",
  "transaction_id": "MGD (Mã giao dịch)",
  "transaction_fee": "Phí giao dịch (VD: 'Miễn phí' hoặc số tiền)"
}}

Tỷ giá: 1 USD = {usd_rate} VND"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            current_app.logger.info(f"Starting AI parsing for OCR text (length: {len(ocr_text)} chars)")
            
            response = cls._get_completion(messages, temperature=0.1, max_tokens=1000)
            
            current_app.logger.info(f"AI Response received (length: {len(response)} chars)")
            current_app.logger.info(f"AI Response preview: {response[:300]}...")  # Log first 300 chars
            
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith('```'):
                response = re.sub(r'^```json?\n', '', response)
                response = re.sub(r'\n```$', '', response)
            
            # Parse JSON
            parsed_data = json.loads(response)
            
            # Validate and ensure all fields exist
            required_fields = [
                'sender_name', 'receiver_name', 'amount_vnd', 'amount_usd',
                'time', 'time_in_seconds', 'date', 'transaction_content',
                'sender_bank', 'receiver_bank', 'transaction_id', 'transaction_fee'
            ]
            
            for field in required_fields:
                if field not in parsed_data:
                    parsed_data[field] = None
            
            current_app.logger.info("AI parsing successful!")
            return {
                'success': True,
                'data': parsed_data,
                'raw_text': ocr_text
            }
            
        except ValueError as e:
            # This catches errors from _get_completion (API errors)
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
