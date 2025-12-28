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

QUAN TRỌNG - Trích xuất 7 thông tin sau:
1. amt (số tiền VND) - Bắt buộc phải là số nguyên, không dấu phẩy/chấm
2. gender (giới tính) - Chỉ "Nam" hoặc "Nữ", phải viết hoa chữ cái đầu
3. category (loại giao dịch) - Dựa vào nội dung để xếp loại
4. transaction_time (thời gian giao dịch) - Format HH:MM:SS (ví dụ: 13:05:02)
5. transaction_day (ngày trong tuần) - **QUAN TRỌNG**: 
   - Tìm ngày tháng năm trong văn bản (ví dụ: "15/10/2024", "15-10-2024", "15 Oct 2024", "Thứ 3, 15/10/2024")
   - Tính toán thứ trong tuần dựa trên ngày đó: 0=Thứ 2, 1=Thứ 3, 2=Thứ 4, 3=Thứ 5, 4=Thứ 6, 5=Thứ 7, 6=Chủ nhật
   - VÍ DỤ: "15/10/2024" là Thứ 3 → trả về 1
   - VÍ DỤ: "20/10/2024" là Chủ nhật → trả về 6
   - VÍ DỤ: "14/10/2024" là Thứ 2 → trả về 0
   - Nếu không tìm thấy ngày tháng năm, để null
6. city (tỉnh/thành phố) - Tên tỉnh/thành phố VN (viết thường, không dấu)
7. age (tuổi) - Tuổi của người giao dịch (18-100), nếu không có thông tin thì mặc định 18

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

DANH SÁCH CITY (tỉnh/thành phố VN) hợp lệ:
ha noi, hanoi, ho chi minh, hcm, hai phong, da nang, can tho, an giang, ba ria vung tau, 
bac giang, bac kan, bac lieu, bac ninh, ben tre, binh dinh, binh duong, binh phuoc, 
binh thuan, ca mau, cao bang, dak lak, dak nong, dien bien, dong nai, dong thap, gia lai, 
ha giang, ha nam, ha tinh, hai duong, hau giang, hoa binh, hung yen, khanh hoa, kien giang, 
kon tum, lai chau, lam dong, lang son, lao cai, long an, nam dinh, nghe an, ninh binh, 
ninh thuan, phu tho, phu yen, quang binh, quang nam, quang ngai, quang ninh, quang tri, 
soc trang, son la, tay ninh, thai binh, thai nguyen, thanh hoa, thua thien hue, tien giang, 
tra vinh, tuyen quang, vinh long, vinh phuc, yen bai

LƯU Ý:
- Nếu không tìm thấy thông tin gender, mặc định là null
- Nếu không xác định được category, mặc định là 'khác'
- Số tiền (amt) phải là số nguyên VND, không có dấu
- Thời gian (transaction_time) phải theo format HH:MM:SS (giờ:phút:giây)
- transaction_day: 0=Thứ 2, 1=Thứ 3, 2=Thứ 4, 3=Thứ 5, 4=Thứ 6, 5=Thứ 7, 6=Chủ nhật
- city: Phải viết thường, không dấu, phải nằm trong danh sách city hợp lệ. Nếu không xác định được thì để null
- age: Nếu có thông tin về tuổi/năm sinh trong văn bản thì tính tuổi, nếu không có thì mặc định 18
- TUYỆT ĐỐI CHỈ TRẢ VỀ JSON, KHÔNG TEXT THỪA"""

        user_prompt = f"""Phân tích văn bản giao dịch sau và trích xuất 7 thông tin:

{ocr_text}

QUAN TRỌNG: Trả về JSON với CẤU TRÚC CHÍNH XÁC SAU (KHÔNG thay đổi tên key):
{{
  "amt": <số tiền VND - số nguyên, VD: 500000>,
  "gender": "<Nam hoặc Nữ hoặc null>",
  "category": "<loại giao dịch>",
  "transaction_time": "<HH:MM:SS - VD: 13:05:02>",
  "transaction_day": <0-6, 0=Thứ 2, 6=Chủ nhật>,
  "city": "<tên tỉnh/thành phố VN, viết thường không dấu>",
  "age": <tuổi 18-100, mặc định 18 nếu không có thông tin>
}}

VÍ DỤ OUTPUT ĐÚNG:
{{
  "amt": 500000,
  "gender": "Nam",
  "category": "xăng dầu",
  "transaction_time": "13:05:02",
  "transaction_day": 5,
  "city": "ha noi",
  "age": 28
}}

VÍ DỤ CÁCH TÍNH transaction_day:
- Văn bản: "Giao dịch ngày 15/10/2024 lúc 13:05:02" → 15/10/2024 là Thứ 3 → transaction_day = 1
- Văn bản: "20-10-2024 15:30:00" → 20/10/2024 là Chủ nhật → transaction_day = 6
- Văn bản: "Thứ 2, 14/10/2024" → Thứ 2 → transaction_day = 0
- Văn bản: "Số tiền: 500.000đ, thời gian: 13:05" (KHÔNG có ngày) → transaction_day = null

CHÚ Ý:
- amt PHẢI là số nguyên VND (ví dụ: 500000, không phải "500,000" hay "500.000")
- gender CHỈ có thể là "Nam", "Nữ" hoặc null
- category PHẢI chọn từ danh sách category hợp lệ ở trên
- transaction_time PHẢI có key chính xác là "transaction_time" và format "HH:MM:SS" (ví dụ: "13:05:02", "09:30:15")
- transaction_day PHẢI tính toán từ ngày tháng năm trong văn bản:
  * TÌM ngày tháng năm (ví dụ: "15/10/2024", "15-10-2024", "Thứ 3 15/10/2024")
  * TÍNH thứ trong tuần: 0=Thứ 2, 1=Thứ 3, 2=Thứ 4, 3=Thứ 5, 4=Thứ 6, 5=Thứ 7, 6=Chủ nhật
  * VÍ DỤ CÁCH TÍNH:
    - "14/10/2024" (hoặc "14-10-2024" hoặc "14 Oct 2024") → Thứ 2 → transaction_day = 0
    - "15/10/2024" → Thứ 3 → transaction_day = 1
    - "16/10/2024" → Thứ 4 → transaction_day = 2
    - "20/10/2024" → Chủ nhật → transaction_day = 6
  * Nếu văn bản có ghi "Thứ 3", "Thứ Tư", "Chủ nhật" thì dùng trực tiếp
  * Nếu KHÔNG có ngày tháng năm trong văn bản, để null
- city PHẢI viết thường, không dấu, thuộc danh sách tỉnh/thành VN (ha noi, ho chi minh, da nang, etc.)
- age PHẢI là số nguyên 18-100, nếu không có thông tin thì để 18"""

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
            required_fields = ['amt', 'gender', 'category', 'transaction_time', 
                             'transaction_day', 'city', 'age']
            
            for field in required_fields:
                if field not in parsed_data:
                    # Set defaults for new fields
                    if field == 'transaction_day':
                        parsed_data[field] = None
                    elif field == 'city':
                        parsed_data[field] = None
                    elif field == 'age':
                        parsed_data[field] = 18  # Default age
                    else:
                        parsed_data[field] = None
            
            # Additional validation
            valid_categories = [
                'giải trí', 'ăn uống', 'xăng dầu', 'siêu thị online', 'siêu thị',
                'sức khỏe', 'nội thất', 'trẻ em', 'khác online', 'khác',
                'chăm sóc cá nhân', 'mua sắm online', 'mua sắm', 'du lịch'
            ]
            
            # Valid cities (63 provinces & cities of Vietnam)
            valid_cities = [
                'ha noi', 'hanoi', 'ho chi minh', 'hcm', 'hai phong', 'da nang', 'can tho',
                'an giang', 'ba ria vung tau', 'bac giang', 'bac kan', 'bac lieu', 'bac ninh',
                'ben tre', 'binh dinh', 'binh duong', 'binh phuoc', 'binh thuan', 'ca mau',
                'cao bang', 'dak lak', 'dak nong', 'dien bien', 'dong nai', 'dong thap',
                'gia lai', 'ha giang', 'ha nam', 'ha tinh', 'hai duong', 'hau giang',
                'hoa binh', 'hung yen', 'khanh hoa', 'kien giang', 'kon tum', 'lai chau',
                'lam dong', 'lang son', 'lao cai', 'long an', 'nam dinh', 'nghe an',
                'ninh binh', 'ninh thuan', 'phu tho', 'phu yen', 'quang binh', 'quang nam',
                'quang ngai', 'quang ninh', 'quang tri', 'soc trang', 'son la', 'tay ninh',
                'thai binh', 'thai nguyen', 'thanh hoa', 'thua thien hue', 'tien giang',
                'tra vinh', 'tuyen quang', 'vinh long', 'vinh phuc', 'yen bai'
            ]
            
            # Ensure category is valid, default to 'khác' if not
            if parsed_data.get('category') not in valid_categories:
                current_app.logger.warning(f"Invalid category '{parsed_data.get('category')}', defaulting to 'khác'")
                parsed_data['category'] = 'khác'
            
            # Ensure gender is valid
            if parsed_data.get('gender') and parsed_data['gender'] not in ['Nam', 'Nữ']:
                current_app.logger.warning(f"Invalid gender '{parsed_data.get('gender')}', setting to null")
                parsed_data['gender'] = None
            
            # Validate city
            if parsed_data.get('city'):
                city_lower = str(parsed_data['city']).lower().strip()
                if city_lower not in valid_cities:
                    current_app.logger.warning(f"Invalid city '{parsed_data.get('city')}', setting to null")
                    parsed_data['city'] = None
                else:
                    parsed_data['city'] = city_lower  # Normalize to lowercase
            
            # Validate transaction_day (0-6)
            if parsed_data.get('transaction_day') is not None:
                try:
                    day = int(parsed_data['transaction_day'])
                    if not (0 <= day <= 6):
                        current_app.logger.warning(f"Invalid transaction_day '{day}', must be 0-6, setting to null")
                        parsed_data['transaction_day'] = None
                    else:
                        parsed_data['transaction_day'] = day
                except (ValueError, TypeError):
                    current_app.logger.warning(f"Invalid transaction_day '{parsed_data.get('transaction_day')}', setting to null")
                    parsed_data['transaction_day'] = None
            
            # Validate age (18-100)
            if parsed_data.get('age') is not None:
                try:
                    age = int(parsed_data['age'])
                    if not (18 <= age <= 100):
                        current_app.logger.warning(f"Invalid age '{age}', must be 18-100, defaulting to 18")
                        parsed_data['age'] = 18
                    else:
                        parsed_data['age'] = age
                except (ValueError, TypeError):
                    current_app.logger.warning(f"Invalid age '{parsed_data.get('age')}', defaulting to 18")
                    parsed_data['age'] = 18
            else:
                parsed_data['age'] = 18  # Default age
            
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
    def _filter_features_for_explanation(cls, transaction_data):
        """Keep only allowed fields for fraud explanation (ignore amt_usd, transaction_month)."""
        if not isinstance(transaction_data, dict):
            return {}

        allowlist = {
            'amt_vnd',
            'gender',
            'category',
            'transaction_hour',
            'transaction_day',
            'age',
            'city',
            'city_pop',
            # Grounding evidence from the model (optional)
            'model_top_factors'
        }

        filtered = {k: transaction_data.get(k) for k in allowlist if k in transaction_data}

        # Sanitize model_top_factors so the LLM can map them back to user fields
        if isinstance(filtered.get('model_top_factors'), list):
            allowed_factor_fields = {
                'amt_vnd',
                'gender',
                'category',
                'transaction_hour',
                'transaction_day',
                'age',
                'city_pop',
            }
            cleaned = []
            for f in filtered['model_top_factors']:
                if not isinstance(f, dict):
                    continue
                feat = str(f.get('feature', '')).strip()
                if feat == 'amt':
                    feat = 'amt_vnd'
                if feat == 'transaction_month':
                    continue
                if feat not in allowed_factor_fields:
                    continue
                cleaned.append({
                    'feature': feat,
                    'feature_vi': f.get('feature_vi'),
                    'raw_value': f.get('raw_value'),
                    'contribution': f.get('contribution'),
                    'direction': f.get('direction'),
                })
            filtered['model_top_factors'] = cleaned

        # Normalize types when possible
        try:
            if 'amt_vnd' in filtered and filtered['amt_vnd'] is not None:
                filtered['amt_vnd'] = float(filtered['amt_vnd'])
        except Exception:
            pass

        for key in ('transaction_hour', 'transaction_day', 'age'):
            try:
                if key in filtered and filtered[key] is not None:
                    filtered[key] = int(filtered[key])
            except Exception:
                pass

        try:
            if 'city_pop' in filtered and filtered['city_pop'] is not None:
                filtered['city_pop'] = int(filtered['city_pop'])
        except Exception:
            pass

        return filtered
    
    @classmethod
    def explain_prediction(cls, prediction_result, transaction_data, explanation_detail: str = "full"):
        """
        Generate human-readable explanation for a model prediction
        
        Args:
            prediction_result (dict): Model prediction output
            transaction_data (dict): Transaction details
            
        Returns:
            str: Natural language explanation
        """
        is_fraud = bool(prediction_result.get('is_fraud', False))
        probability = prediction_result.get('fraud_probability', 0)

        try:
            probability = float(probability)
        except Exception:
            probability = 0.0

        filtered = cls._filter_features_for_explanation(transaction_data)

        detail = (explanation_detail or "full").strip().lower()
        if detail not in ("short", "full"):
            detail = "full"

        system_prompt = (
            "Bạn là trợ lý giải thích kết quả phát hiện gian lận thẻ tín dụng. "
            "Bạn KHÔNG được giả vờ biết trọng số, feature importance hay logic nội bộ của mô hình. "
            "Chỉ được suy luận hợp lý dựa trên (1) dữ liệu đầu vào được cung cấp và (2) kết quả dự đoán. "
            "Nếu thiếu dữ liệu thì nói rõ là thiếu."
        )

        if detail == "short":
            user_prompt = f"""Hãy giải thích NGẮN GỌN cho giao diện điện thoại.

Kết quả mô hình:
- is_fraud: {is_fraud}
- fraud_probability: {probability:.4f}

Chỉ dùng các trường input sau để giải thích (bỏ qua các trường khác như transaction_month, amt_usd):
{json.dumps(filtered, ensure_ascii=False)}

Nếu có trường `model_top_factors` thì đó là bằng chứng từ mô hình (đóng góp từng feature). Bạn PHẢI dựa vào nó để nêu nguyên nhân cụ thể (ví dụ: contribution dương => tăng rủi ro fraud).

Yêu cầu trả lời (tối đa ~6 dòng):
1) 1 câu tóm tắt.
2) Lý do chính: đúng 2 bullet (mỗi bullet nêu rõ 1 field trong input). Nếu có contribution, chỉ nêu 1 con số lớn nhất.
3) Khuyến nghị: đúng 2 bullet.

Lưu ý:
- Nếu is_fraud=false, giải thích ngắn gọn rằng không cần phân tích sâu.
- Nếu is_fraud=true, tập trung nêu các yếu tố có thể làm tăng rủi ro dựa trên input."""

            max_tokens = 220
        else:
            user_prompt = f"""Hãy giải thích cho người dùng không chuyên về kết quả phát hiện gian lận.

Kết quả mô hình:
- is_fraud: {is_fraud}
- fraud_probability: {probability:.4f}

Chỉ dùng các trường input sau để giải thích (bỏ qua các trường khác như transaction_month, amt_usd):
{json.dumps(filtered, ensure_ascii=False)}

Nếu có trường `model_top_factors` thì đó là bằng chứng từ mô hình (đóng góp từng feature). Bạn PHẢI dựa vào nó để nêu nguyên nhân cụ thể (ví dụ: contribution dương => tăng rủi ro fraud).

Yêu cầu trả lời:
1) Tóm tắt (1-2 câu)
2) Nguyên nhân/động lực chính (bullet list):
    - Ít nhất 3 bullet.
    - Mỗi bullet bắt buộc nêu rõ 1 field cụ thể trong input (amt_vnd/transaction_hour/transaction_day/age/city/city_pop/gender/category).
    - Nếu có `model_top_factors`, hãy ưu tiên các feature có |contribution| lớn và giải thích theo hướng: contribution dương => tăng rủi ro.
3) Khuyến nghị (2-4 bullet)

Lưu ý:
- Nếu is_fraud=false, giải thích ngắn gọn rằng không cần phân tích sâu.
- Nếu is_fraud=true, tập trung nêu các yếu tố có thể làm tăng rủi ro dựa trên input."""

            max_tokens = 550

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return cls._get_completion(messages, temperature=0.2, max_tokens=max_tokens)
    
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
