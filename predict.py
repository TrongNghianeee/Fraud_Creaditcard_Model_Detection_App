"""
FRAUD DETECTION PREDICTION SCRIPT - MODEL FA
Sử dụng model fraud_detection_fa_smoteenn.pkl để dự đoán giao dịch gian lận

FEATURES được FA chọn (9 features):
✅ amt            → Số tiền (VND → USD conversion)
✅ gender         → Giới tính (Nam/Nữ → M/F mapping)
✅ category       → Loại giao dịch (Tiếng Việt → English mapping)
✅ lat            → Vĩ độ (unknown nếu không có)
✅ merch_long     → Kinh độ merchant (unknown nếu không có)
✅ transaction_hour → Giờ giao dịch (0-23, chuẩn hóa)
✅ merchant       → Merchant (unknown)
✅ street         → Street (unknown)
✅ city           → City (unknown)
✅ zip            → Zip code (unknown)

Note: Các features khó convert VN→US sẽ để 'unknown'
"""

import pandas as pd
import numpy as np
import joblib
import warnings
from datetime import datetime
from typing import Dict, Union
from dataclasses import dataclass
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings("ignore")


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class FAConfig:
    """Configuration cho Feature Selection (Firefly Algorithm)"""
    
    # Feature selection parameters
    selection_ratio: float = 0.7
    min_feature_ratio: float = 0.6
    max_feature_ratio: float = 0.8
    min_feature_count: int = 8
    
    # Random seed
    random_state: int = 42
    
    # Selection mode
    feature_selection_mode: str = "random"
    
    # Advanced options
    n_fireflies: int = 30
    n_epochs: int = 15
    alpha: float = 0.25
    beta0: float = 2.0
    gamma: float = 0.20
    lambda_feat: float = 0.01
    diversity_threshold: float = 0.1
    patience: int = 6
    validation_strictness: float = 0.8
    overfitting_threshold: float = 0.03


# ============================================================================
# CUSTOM TRANSFORMERS (Required for loading pickled model)
# ============================================================================

class DateFeatureExtractor(BaseEstimator, TransformerMixin):
    """Extract features từ datetime columns"""
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        X = X.copy()
        
        # Convert datetime
        X['trans_date_trans_time'] = pd.to_datetime(X['trans_date_trans_time'])
        X['dob'] = pd.to_datetime(X['dob'])
        
        # Extract features
        X['transaction_hour'] = X['trans_date_trans_time'].dt.hour
        X['transaction_day'] = X['trans_date_trans_time'].dt.dayofweek
        X['transaction_month'] = X['trans_date_trans_time'].dt.month
        X['age'] = (X['trans_date_trans_time'] - X['dob']).dt.days // 365
        
        # Drop original datetime columns
        X.drop(['trans_date_trans_time', 'dob', 'unix_time'], axis=1, inplace=True, errors='ignore')
        
        return X


class CategoricalEncoder(BaseEstimator, TransformerMixin):
    """Encode categorical features"""
    
    def __init__(self):
        self.label_encoders = {}
    
    def fit(self, X, y=None):
        X = X.copy()
        
        # Identify categorical columns
        cat_cols = X.select_dtypes(include=['object']).columns.tolist()
        
        # Fit label encoders
        for col in cat_cols:
            le = LabelEncoder()
            # Handle missing values
            X[col] = X[col].fillna('unknown')
            le.fit(X[col].astype(str))
            self.label_encoders[col] = le
        
        return self
    
    def transform(self, X):
        X = X.copy()
        
        # Transform using fitted encoders
        for col, le in self.label_encoders.items():
            if col in X.columns:
                # Fill missing values with first class
                X[col] = X[col].fillna(le.classes_[0])
                
                # Handle unseen categories - use first class as default
                X[col] = X[col].astype(str).apply(
                    lambda x: x if x in le.classes_ else le.classes_[0]
                )
                X[col] = le.transform(X[col])
        
        return X


class MissingValueHandler(BaseEstimator, TransformerMixin):
    """Handle missing values"""
    
    def __init__(self):
        self.fill_values = {}
    
    def fit(self, X, y=None):
        X = X.copy()
        
        # For numeric columns, use median
        num_cols = X.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            self.fill_values[col] = X[col].median()
        
        return self
    
    def transform(self, X):
        X = X.copy()
        
        # Fill numeric missing values
        for col, fill_val in self.fill_values.items():
            if col in X.columns:
                X[col] = X[col].fillna(fill_val)
        
        return X

class FeatureSelector(BaseEstimator, TransformerMixin):
    """Feature Selection using Firefly Algorithm (Simplified for prediction)"""
    
    def __init__(self, selected_features=None):
        """
        Initialize with pre-selected features
        
        Args:
            selected_features: List of feature names to select
        """
        self.selected_features_ = selected_features
        self.feature_names_ = None
    
    def fit(self, X, y=None):
        """Fit - just store feature names"""
        if isinstance(X, pd.DataFrame):
            self.feature_names_ = X.columns.tolist()
        return self
    
    def transform(self, X):
        """Transform by selecting features"""
        if self.selected_features_ is None:
            return X
        
        if isinstance(X, pd.DataFrame):
            return X[self.selected_features_]
        else:
            # Convert to DataFrame for selection
            df = pd.DataFrame(X, columns=self.feature_names_)
            return df[self.selected_features_].values

# ============================================================================
# MAPPING VN → US
# ============================================================================

# Category mapping: Tiếng Việt → English (1 mapping cho mỗi category)
CATEGORY_VN_TO_EN = {
    'giải trí': 'entertainment',
    'ăn uống': 'food_dining',
    'xăng dầu': 'gas_transport',
    'siêu thị online': 'grocery_net',
    'siêu thị': 'grocery_pos',
    'sức khỏe': 'health_fitness',
    'nội thất': 'home',
    'trẻ em': 'kids_pets',
    'khác online': 'misc_net',
    'khác': 'misc_pos',
    'chăm sóc cá nhân': 'personal_care',
    'mua sắm online': 'shopping_net',
    'mua sắm': 'shopping_pos',
    'du lịch': 'travel'
}

# Gender mapping: Tiếng Việt → M/F (1 mapping mỗi loại)
GENDER_VN_TO_EN = {
    'nam': 'M',
    'nữ': 'F'
}

# VND to USD exchange rate
VND_TO_USD_RATE = 25000


def convert_vnd_to_usd(vnd_amount: float) -> float:
    """Convert VND sang USD"""
    return vnd_amount / VND_TO_USD_RATE


def convert_category(category_input: str) -> str:
    """Convert category từ Tiếng Việt hoặc English"""
    category_lower = category_input.lower().strip()
    if category_lower in CATEGORY_VN_TO_EN:
        return CATEGORY_VN_TO_EN[category_lower]
    else:
        raise ValueError(
            f"Category '{category_input}' không hợp lệ.\n"
            f"Valid categories: {list(set(CATEGORY_VN_TO_EN.values()))}"
        )


def convert_gender(gender_input: str) -> str:
    """Convert gender từ Tiếng Việt sang M/F"""
    gender_lower = gender_input.lower().strip()
    if gender_lower in GENDER_VN_TO_EN:
        return GENDER_VN_TO_EN[gender_lower]
    else:
        raise ValueError(
            f"Gender '{gender_input}' không hợp lệ. "
            f"Chỉ chấp nhận: nam/nữ hoặc M/F"
        )


class FraudDetector:
    """
    Class để dự đoán giao dịch gian lận với FA model
    Chỉ sử dụng 9 features được FA chọn
    """
    
    def __init__(self, model_path='fraud_detection_fa_smoteenn.pkl'):
        """
        Load trained model
        
        Args:
            model_path: Đường dẫn tới file .pkl
        """
        print(f"Loading FA model from {model_path}...")
        self.pipeline = joblib.load(model_path)
        print("✅ FA Model loaded successfully!")
        
        # Valid categories (14 loại)
        self.valid_categories = [
            'entertainment', 'food_dining', 'gas_transport', 'grocery_net',
            'grocery_pos', 'health_fitness', 'home', 'kids_pets',
            'misc_net', 'misc_pos', 'personal_care', 'shopping_net',
            'shopping_pos', 'travel'
        ]
        
        self.valid_genders = ['M', 'F']
        
        # Default values - SỬ DỤNG GIÁ TRỊ PHỔ BIẾN NHẤT trong training data
        # Không dùng 'unknown' vì không có trong training data
        self.default_values = {
            'merchant': 'fraud_Kirlin and Sons',  # Merchant phổ biến trong data
            'street': 'Main St',                   # Street phổ biến
            'city': 'Houston',                     # City lớn có trong data
            'state': 'TX',                         # State phổ biến
            'zip': 77001,                          # Zip code Houston
            'job': 'Food service',                 # Job phổ biến
            'lat': 29.7604,                        # Houston lat
            'long': -95.3698,                      # Houston long
            'city_pop': 2296224,                   # Houston population
            'merch_lat': 29.7604,
            'merch_long': -95.3698,
            'trans_date_trans_time': None,
            'dob': None,
            'age': 35
        }
    
    def validate_and_convert_input(self, user_input: Dict) -> Dict:
        """
        Validate và convert input từ VN → US format
        
        Required fields:
        - category (VN hoặc EN)
        - amt (VND)
        - gender (nam/nữ hoặc M/F)
        - transaction_hour (0-23)
        
        Optional fields:
        - lat, merch_long (nếu không có → 0.0)
        - merchant, street, city, zip (nếu không có → 'unknown')
        
        Args:
            user_input: Dict chứa input từ người dùng
            
        Returns:
            Dict đã được validate và convert
        """
        errors = []
        converted = {}
        
        # Required fields - 4 features BẮT BUỘC
        required_fields = ['category', 'amt', 'gender', 'transaction_hour']
        
        for field in required_fields:
            if field not in user_input:
                errors.append(f"Missing required field: {field}")
        
        if errors:
            raise ValueError(f"Input validation errors:\n" + "\n".join(errors))
        
        # ===== CONVERT CATEGORY (Tiếng Việt → English) =====
        try:
            converted['category'] = convert_category(user_input['category'])
            if converted['category'] not in self.valid_categories:
                raise ValueError(f"Category không hợp lệ: {converted['category']}")
        except Exception as e:
            raise ValueError(f"Category error: {str(e)}")
        
        # ===== CONVERT AMT (VND → USD) =====
        try:
            vnd_amount = float(user_input['amt'])
            if vnd_amount <= 0:
                raise ValueError(f"Amount phải > 0, got: {vnd_amount}")
            converted['amt'] = convert_vnd_to_usd(vnd_amount)
            converted['_vnd_amount'] = vnd_amount  # Store for display
            
            if vnd_amount > 250_000_000:  # > 250 triệu VND
                print(f"⚠️  Warning: Amount {vnd_amount:,} VND (${converted['amt']:.2f}) rất lớn!")
        except Exception as e:
            raise ValueError(f"Amount error: {str(e)}")
        
        # ===== CONVERT GENDER (nam/nữ → M/F) =====
        try:
            converted['gender'] = convert_gender(user_input['gender'])
        except Exception as e:
            raise ValueError(f"Gender error: {str(e)}")
        
        # ===== VALIDATE TRANSACTION_HOUR =====
        try:
            hour = int(user_input['transaction_hour'])
            if not (0 <= hour <= 23):
                raise ValueError(f"transaction_hour phải 0-23, got: {hour}")
            converted['transaction_hour'] = hour
        except Exception as e:
            raise ValueError(f"Transaction hour error: {str(e)}")
        
        # ===== OPTIONAL: lat, merch_long =====
        converted['lat'] = float(user_input.get('lat', 0.0))
        converted['merch_long'] = float(user_input.get('merch_long', 0.0))
        
        # ===== OPTIONAL: merchant, street, city, zip =====
        # Nếu user không cung cấp, để là None/np.nan (không ghi giá trị cụ thể)
        # -> pipeline sẽ xử lý missing values (MissingValueHandler / CategoricalEncoder)
        converted['merchant'] = user_input.get('merchant', None)
        converted['street'] = user_input.get('street', None)
        converted['city'] = user_input.get('city', None)
        converted['zip'] = user_input.get('zip', None)
        
        return converted
    
    def prepare_input_dataframe(self, user_input: Dict) -> pd.DataFrame:
        """
        Chuyển input đã convert thành DataFrame cho model
        Chỉ sử dụng 9 features FA chọn + các features khác để 'unknown' hoặc default
        
        Args:
            user_input: Dict đã được validate và convert
            
        Returns:
            DataFrame 1 row với tất cả features
        """
        # Validate và convert input
        converted = self.validate_and_convert_input(user_input)
        
        # Tạo transaction time từ hour
        now = datetime.now()
        transaction_date = now.replace(
            hour=converted['transaction_hour'], 
            minute=0, 
            second=0, 
            microsecond=0
        )
        
        # Tính DOB từ default age
        dob = datetime(now.year - self.default_values['age'], now.month, now.day)
        
        # Tạo DataFrame với TẤT CẢ features THEO ĐÚNG THỨ TỰ TRAINING
        # Thứ tự: cc_num, merchant, category, amt, first, last, gender, street, 
        #         city, state, zip, lat, long, city_pop, job, merch_lat, merch_long,
        #         trans_date_trans_time, dob
        data = {
            # Feature 0-2
            'cc_num': 1234567890123456,               # Dummy (FA loại bỏ)
            'merchant': converted['merchant'],        # ✅ FA selected
            'category': converted['category'],        # ✅ FA selected, Converted VN→EN
            
            # Feature 3
            'amt': converted['amt'],                  # ✅ FA selected, Converted VND→USD
            
            # Feature 4-6
            'first': 'John',                          # Dummy (FA loại bỏ)
            'last': 'Doe',                            # Dummy (FA loại bỏ)
            'gender': converted['gender'],            # ✅ FA selected, Converted nam/nữ→M/F
            
            # Feature 7-10
            'street': converted['street'],            # ✅ FA selected
            'city': converted['city'],                # ✅ FA selected
            'state': self.default_values['state'],    # Default (FA loại bỏ)
            'zip': converted['zip'],                  # ✅ FA selected
            
            # Feature 11-14
            'lat': converted['lat'],                  # ✅ FA selected
            'long': self.default_values['long'],      # Default (FA loại bỏ)
            'city_pop': self.default_values['city_pop'],  # Default (FA loại bỏ)
            'job': self.default_values['job'],        # Default (FA loại bỏ)
            
            # Feature 15-16
            'merch_lat': converted.get('merch_lat', self.default_values['merch_lat']),
            'merch_long': converted['merch_long'],    # ✅ FA selected
            
            # Datetime features (sẽ extract thành transaction_hour, transaction_day, transaction_month, age)
            'trans_date_trans_time': transaction_date,
            'dob': dob
        }
        
        df = pd.DataFrame([data])
        
        return df, converted
    
    def predict(self, user_input: Dict, return_proba=True) -> Dict:
        """
        Dự đoán giao dịch có phải gian lận không
        
        Args:
            user_input: Dict chứa input từ người dùng (VN format)
                Required: category, amt (VND), gender, transaction_hour
                Optional: lat, merch_long, merchant, street, city, zip
            return_proba: Có trả về probability không
            
        Returns:
            Dict chứa kết quả dự đoán
        """
        # Prepare input
        X, converted = self.prepare_input_dataframe(user_input)
        
        print("\n" + "="*60)
        print("INPUT SUMMARY (9 FA-Selected Features)")
        print("="*60)
        print(f"✅ Category:         {converted['category']} (từ '{user_input['category']}')")
        print(f"✅ Amount:           {converted.get('_vnd_amount', 0):,.0f} VND → ${converted['amt']:.2f} USD")
        print(f"✅ Gender:           {converted['gender']} (từ '{user_input['gender']}')")
        print(f"✅ Transaction Hour: {converted['transaction_hour']}:00")
        print(f"✅ Latitude:         {converted['lat']}")
        print(f"✅ Merchant Long:    {converted['merch_long']}")
        
        # Show indication if optional values were not provided
        merchant_display = converted['merchant'] if converted['merchant'] is not None else '---'
        if 'merchant' not in user_input:
            merchant_display += " (not provided)"
        print(f"✅ Merchant:         {merchant_display}")
        
        street_display = converted['street'] if converted['street'] is not None else '---'
        if 'street' not in user_input:
            street_display += " (not provided)"
        print(f"✅ Street:           {street_display}")
        
        city_display = converted['city'] if converted['city'] is not None else '---'
        if 'city' not in user_input:
            city_display += " (not provided)"
        print(f"✅ City:             {city_display}")
        
        print(f"✅ Zip:              {converted['zip']}")
        
        # Predict
        prediction = self.pipeline.predict(X)[0]
        
        result = {
            'is_fraud': bool(prediction),
            'prediction': int(prediction)
        }
        
        if return_proba:
            proba = self.pipeline.predict_proba(X)[0]
            result['fraud_probability'] = float(proba[1])
            result['safe_probability'] = float(proba[0])
        
        # Print result
        print("\n" + "="*60)
        print("PREDICTION RESULT")
        print("="*60)
        
        if result['is_fraud']:
            print("⚠️  FRAUD DETECTED!")
            print(f"🚨 Fraud Probability: {result['fraud_probability']*100:.2f}%")
        else:
            print("✅ LEGITIMATE TRANSACTION")
            print(f"✓  Safe Probability: {result['safe_probability']*100:.2f}%")
        
        print("="*60 + "\n")
        
        return result
    
    def predict_batch(self, transactions: list) -> list:
        """
        Dự đoán cho nhiều giao dịch cùng lúc
        
        Args:
            transactions: List of Dict, mỗi dict là 1 giao dịch
            
        Returns:
            List of Dict kết quả dự đoán
        """
        results = []
        
        for i, transaction in enumerate(transactions, 1):
            print(f"\n{'='*60}")
            print(f"Processing transaction {i}/{len(transactions)}")
            print(f"{'='*60}")
            
            try:
                result = self.predict(transaction)
                results.append(result)
            except Exception as e:
                print(f"❌ Error processing transaction {i}: {str(e)}")
                results.append({'error': str(e)})
        
        return results


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_single_prediction():
    """
    Ví dụ dự đoán 1 giao dịch - Input VN format
    """
    print("\n" + "="*80)
    print(" EXAMPLE: SINGLE TRANSACTION PREDICTION (VN Input Format) ")
    print("="*80 + "\n")
    
    # Load model
    detector = FraudDetector(model_path='fraud_detection_fa_smoteenn.pkl')
    
    # User input - VN FORMAT (Tiếng Việt + VND)
    # CHỈ CẦN 4 FIELDS BẮT BUỘC - các field khác sẽ dùng default từ training data
    user_transaction = {
        'category': 'xăng dầu',          # Tiếng Việt OK
        'amt': 500_000,                   # VND
        'gender': 'nam',                  # Tiếng Việt OK
        'transaction_hour': 7,            # 7 AM
        # Optional fields (có thể bỏ qua, sẽ dùng default values)
        # 'lat': 21.0285,                 # Vĩ độ (optional)
        # 'merch_long': 105.8542,         # Kinh độ (optional)
        # 'merchant': 'Some Merchant',    # Merchant (optional)
        # 'street': 'Some Street',        # Street (optional)
        # 'city': 'Hanoi',                # City (optional)
        # 'zip': 10000                    # Zip (optional)
    }
    
    # Predict
    result = detector.predict(user_transaction)
    
    return result


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    """
    Chạy các ví dụ hoặc interactive mode
    """
    
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == 'single':
            example_single_prediction()
        elif mode == 'batch':
            example_batch_prediction()
        elif mode == 'interactive':
            interactive_mode()
        else:
            print(f"Unknown mode: {mode}")
            print("Available modes: single, batch, interactive")
    else:
        # Default: Run single example
        print("Running default mode: single prediction example")
        print("Use: python predict.py [single|batch|interactive]")
        example_single_prediction()
