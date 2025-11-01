"""
Fraud Detector Service - Direct Model Prediction
Sử dụng logic từ predict.py để dự đoán fraud trực tiếp
"""
import pandas as pd
import numpy as np
import joblib
import warnings
from datetime import datetime
from typing import Dict
from dataclasses import dataclass
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelEncoder
import os

warnings.filterwarnings("ignore")


# ============================================================================
# CONFIGURATION (Required for unpickling model)
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
        self.selected_features_ = selected_features
        self.feature_names_ = None
    
    def fit(self, X, y=None):
        if isinstance(X, pd.DataFrame):
            self.feature_names_ = X.columns.tolist()
        return self
    
    def transform(self, X):
        if self.selected_features_ is None:
            return X
        
        if isinstance(X, pd.DataFrame):
            return X[self.selected_features_]
        else:
            df = pd.DataFrame(X, columns=self.feature_names_)
            return df[self.selected_features_].values


# ============================================================================
# MAPPING VN → US
# ============================================================================

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

GENDER_VN_TO_EN = {
    'nam': 'M',
    'nữ': 'F'
}

VND_TO_USD_RATE = 25000


class FraudDetectorService:
    """
    Service để dự đoán fraud trực tiếp từ model
    Sử dụng 4 trường: amt (VND), gender (Nam/Nữ), category (VN), transaction_time (HH:MM:SS)
    """
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FraudDetectorService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            self.load_model()
        
        # Default values từ training data
        self.default_values = {
            'merchant': 'fraud_Kirlin and Sons',
            'street': 'Main St',
            'city': 'Houston',
            'state': 'TX',
            'zip': 77001,
            'job': 'Food service',
            'lat': 29.7604,
            'long': -95.3698,
            'city_pop': 2296224,
            'merch_lat': 29.7604,
            'merch_long': -95.3698,
            'age': 35
        }
    
    def load_model(self):
        """Load model từ file"""
        # IMPORTANT: Register custom transformers in sys.modules
        # để joblib.load() có thể tìm thấy các class khi unpickle
        import sys
        
        # Register trong module hiện tại
        current_module = sys.modules[__name__]
        current_module.FAConfig = FAConfig
        current_module.DateFeatureExtractor = DateFeatureExtractor
        current_module.CategoricalEncoder = CategoricalEncoder
        current_module.MissingValueHandler = MissingValueHandler
        current_module.FeatureSelector = FeatureSelector
        
        # Cũng register trong __main__ để tương thích
        import __main__
        __main__.FAConfig = FAConfig
        __main__.DateFeatureExtractor = DateFeatureExtractor
        __main__.CategoricalEncoder = CategoricalEncoder
        __main__.MissingValueHandler = MissingValueHandler
        __main__.FeatureSelector = FeatureSelector
        
        model_path = os.path.join('models', 'fraud_detection_fa_smoteenn.pkl')
        
        if not os.path.exists(model_path):
            # Fallback to fraud_model_v2_flexible.pkl
            model_path = os.path.join('models', 'fraud_model_v2_flexible.pkl')
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
        
        print(f"Loading fraud detection model from {model_path}...")
        self._model = joblib.load(model_path)
        print("✅ Model loaded successfully!")
    
    def convert_vnd_to_usd(self, vnd_amount: float) -> float:
        """Convert VND sang USD"""
        return vnd_amount / VND_TO_USD_RATE
    
    def convert_category(self, category_vn: str) -> str:
        """Convert category từ Tiếng Việt sang English"""
        category_lower = category_vn.lower().strip()
        return CATEGORY_VN_TO_EN.get(category_lower, 'misc_pos')
    
    def convert_gender(self, gender_vn: str) -> str:
        """Convert gender từ Tiếng Việt sang M/F"""
        gender_lower = gender_vn.lower().strip()
        return GENDER_VN_TO_EN.get(gender_lower, 'M')
    
    def parse_transaction_time(self, time_str: str) -> int:
        """
        Parse transaction_time (HH:MM:SS) thành hour (0-23)
        
        Args:
            time_str: Time string format "HH:MM:SS" (ví dụ: "13:05:02")
            
        Returns:
            int: Hour (0-23)
        """
        try:
            parts = time_str.split(':')
            if len(parts) >= 1:
                hour = int(parts[0])
                if 0 <= hour <= 23:
                    return hour
        except Exception:
            pass
        
        # Default to 12 if parsing fails
        return 12
    
    def prepare_input_dataframe(self, amt_vnd: float, gender_vn: str, 
                                category_vn: str, transaction_time: str) -> pd.DataFrame:
        """
        Chuẩn bị DataFrame input cho model
        
        Args:
            amt_vnd: Số tiền VND
            gender_vn: Giới tính (Nam/Nữ)
            category_vn: Loại giao dịch (Tiếng Việt)
            transaction_time: Thời gian giao dịch (HH:MM:SS)
            
        Returns:
            DataFrame với tất cả features
        """
        # Convert các giá trị
        amt_usd = self.convert_vnd_to_usd(amt_vnd)
        gender_en = self.convert_gender(gender_vn)
        category_en = self.convert_category(category_vn)
        transaction_hour = self.parse_transaction_time(transaction_time)
        
        # Tạo transaction datetime
        now = datetime.now()
        transaction_date = now.replace(
            hour=transaction_hour,
            minute=0,
            second=0,
            microsecond=0
        )
        
        # Tính DOB từ default age
        dob = datetime(now.year - self.default_values['age'], now.month, now.day)
        
        # Tạo DataFrame với TẤT CẢ features theo đúng thứ tự training
        data = {
            'cc_num': 1234567890123456,
            'merchant': self.default_values['merchant'],
            'category': category_en,
            'amt': amt_usd,
            'first': 'John',
            'last': 'Doe',
            'gender': gender_en,
            'street': self.default_values['street'],
            'city': self.default_values['city'],
            'state': self.default_values['state'],
            'zip': self.default_values['zip'],
            'lat': self.default_values['lat'],
            'long': self.default_values['long'],
            'city_pop': self.default_values['city_pop'],
            'job': self.default_values['job'],
            'merch_lat': self.default_values['merch_lat'],
            'merch_long': self.default_values['merch_long'],
            'trans_date_trans_time': transaction_date,
            'dob': dob
        }
        
        df = pd.DataFrame([data])
        
        return df, {
            'amt_vnd': amt_vnd,
            'amt_usd': amt_usd,
            'gender_vn': gender_vn,
            'gender_en': gender_en,
            'category_vn': category_vn,
            'category_en': category_en,
            'transaction_time': transaction_time,
            'transaction_hour': transaction_hour
        }
    
    def predict(self, amt: float, gender: str, category: str, 
                transaction_time: str) -> Dict:
        """
        Dự đoán fraud cho giao dịch
        
        Args:
            amt: Số tiền VND
            gender: Giới tính (Nam/Nữ)
            category: Loại giao dịch (Tiếng Việt)
            transaction_time: Thời gian (HH:MM:SS)
            
        Returns:
            Dict chứa kết quả dự đoán
        """
        # Prepare input
        X, converted = self.prepare_input_dataframe(amt, gender, category, transaction_time)
        
        # Predict
        prediction = self._model.predict(X)[0]
        proba = self._model.predict_proba(X)[0]
        
        result = {
            'is_fraud': bool(prediction),
            'fraud_probability': float(proba[1]),
            'safe_probability': float(proba[0]),
            'prediction': int(prediction),
            'input_converted': converted
        }
        
        return result


# Singleton instance
fraud_detector = FraudDetectorService()
