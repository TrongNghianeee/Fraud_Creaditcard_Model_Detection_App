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

# Province population lookup (Vietnam - 63 provinces & cities)
PROVINCE_POPULATION = {
    'ha noi': 8054000, 'hanoi': 8054000, 'ho chi minh': 8993000, 'hcm': 9000000,
    'hai phong': 2029000, 'da nang': 1135000, 'can tho': 1238000, 'an giang': 1908000,
    'ba ria vung tau': 1148000, 'bac giang': 1803000, 'bac kan': 313000, 'bac lieu': 902000,
    'bac ninh': 1368000, 'ben tre': 1260000, 'binh dinh': 1501000, 'binh duong': 2426000,
    'binh phuoc': 993000, 'binh thuan': 1226000, 'ca mau': 1217000, 'cao bang': 530000,
    'dak lak': 1912000, 'dak nong': 613000, 'dien bien': 598000, 'dong nai': 3097000,
    'dong thap': 1676000, 'gia lai': 1513000, 'ha giang': 854000, 'ha nam': 820000,
    'ha tinh': 1270000, 'hai duong': 1892000, 'hau giang': 769000, 'hoa binh': 854000,
    'hung yen': 1282000, 'khanh hoa': 1233000, 'kien giang': 1875000, 'kon tum': 530000,
    'lai chau': 460000, 'lam dong': 1296000, 'lang son': 789000, 'lao cai': 730000,
    'long an': 1688000, 'nam dinh': 1780000, 'nghe an': 3327000, 'ninh binh': 982000,
    'ninh thuan': 590000, 'phu tho': 1470000, 'phu yen': 877000, 'quang binh': 912000,
    'quang nam': 1495000, 'quang ngai': 1255000, 'quang ninh': 1320000, 'quang tri': 632000,
    'soc trang': 1295000, 'son la': 1248000, 'tay ninh': 1167000, 'thai binh': 1868000,
    'thai nguyen': 1286000, 'thanh hoa': 3689000, 'thua thien hue': 1154000,
    'tien giang': 1764000, 'tra vinh': 1015000, 'tuyen quang': 788000,
    'vinh long': 1023000, 'vinh phuc': 1152000, 'yen bai': 820000
}


class FraudDetectorService:
    """
    Service để dự đoán fraud trực tiếp từ model
    Sử dụng 7 trường bắt buộc (theo predict.py):
    - amt (VND): Số tiền
    - gender (Nam/Nữ): Giới tính
    - category (VN): Loại giao dịch
    - transaction_hour (0-23): Giờ giao dịch
    - transaction_day (0-6): Ngày trong tuần
    - age (18-100): Tuổi
    - city (VN province): Thành phố/Tỉnh
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
        
        # Default values cho các fields KHÔNG required
        self.default_values = {
            'merchant': 'fraud_Kirlin and Sons',
            'street': 'Main St',
            'city': 'Houston',
            'state': 'TX',
            'zip': 77001,
            'job': 'Food service',
            'lat': 29.7604,
            'long': -95.3698,
            'merch_lat': 29.7604,
            'merch_long': -95.3698,
            'transaction_month': 6  # Default month
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
    
    def lookup_city_population(self, city_input: str) -> int:
        """
        Lookup city population từ tỉnh/thành phố VN
        
        Args:
            city_input: Tên tỉnh/thành phố (VN)
            
        Returns:
            int: Population (default 1000000 nếu không tìm thấy)
        """
        city_lower = city_input.lower().strip()
        return PROVINCE_POPULATION.get(city_lower, 1000000)
    
    def normalize_hour(self, hour: int) -> int:
        """Normalize hour to 0-23 range"""
        return max(0, min(23, int(hour)))
    
    def normalize_day(self, day: int) -> int:
        """Normalize day to 0-6 range (Monday=0, Sunday=6)"""
        return max(0, min(6, int(day)))
    
    def normalize_month(self, month: int) -> int:
        """Normalize month to 1-12 range"""
        return max(1, min(12, int(month)))
    
    def normalize_age(self, age: int) -> int:
        """Normalize age to 18-100 range"""
        return max(18, min(100, int(age)))
    
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
                                category_vn: str, transaction_hour: int,
                                transaction_day: int, age: int, city: str,
                                city_pop: int, transaction_month: int = None) -> pd.DataFrame:
        """
        Chuẩn bị DataFrame input cho model (theo logic predict.py)
        
        Args:
            amt_vnd: Số tiền VND (REQUIRED)
            gender_vn: Giới tính (Nam/Nữ) (REQUIRED)
            category_vn: Loại giao dịch (Tiếng Việt) (REQUIRED)
            transaction_hour: Giờ giao dịch 0-23 (REQUIRED)
            transaction_day: Ngày trong tuần 0-6, Monday=0 (REQUIRED)
            age: Tuổi 18-100 (REQUIRED)
            city: Thành phố/Tỉnh VN (REQUIRED)
            city_pop: Dân số tỉnh/thành (REQUIRED - app đã lookup)
            transaction_month: Tháng 1-12 (OPTIONAL, default=6)
            
        Returns:
            Tuple (DataFrame, converted_info)
        """
        # Validate amount
        if amt_vnd <= 0:
            raise ValueError("Amount must be positive")
        
        # Validate city_pop
        if city_pop <= 0:
            raise ValueError("City population must be positive")
        
        # Convert & normalize các giá trị
        amt_usd = self.convert_vnd_to_usd(amt_vnd)
        gender_en = self.convert_gender(gender_vn)
        category_en = self.convert_category(category_vn)
        transaction_hour = self.normalize_hour(transaction_hour)
        transaction_day = self.normalize_day(transaction_day)
        age = self.normalize_age(age)
        # city_pop đã được app lookup và truyền vào, không cần lookup nữa
        
        # Optional month with default
        if transaction_month is None:
            transaction_month = self.default_values['transaction_month']
        else:
            transaction_month = self.normalize_month(transaction_month)
        
        # Tạo datetime
        now = datetime.now()
        transaction_date = now.replace(
            hour=transaction_hour,
            minute=0,
            second=0,
            microsecond=0,
            day=1,
            month=transaction_month
        )
        
        # Tính DOB từ age
        dob = datetime(now.year - age, now.month, now.day)
        
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
            'city_pop': city_pop,
            'job': self.default_values['job'],
            'merch_lat': self.default_values['merch_lat'],
            'merch_long': self.default_values['merch_long'],
            'trans_date_trans_time': transaction_date,
            'dob': dob
        }
        
        df = pd.DataFrame([data])
        
        converted_info = {
            'amt_vnd': amt_vnd,
            'amt_usd': amt_usd,
            'gender_vn': gender_vn,
            'gender_en': gender_en,
            'category_vn': category_vn,
            'category_en': category_en,
            'transaction_hour': transaction_hour,
            'transaction_day': transaction_day,
            'transaction_month': transaction_month,
            'age': age,
            'city': city,
            'city_pop': city_pop
        }
        
        return df, converted_info
    
    def predict(self, amt: float, gender: str, category: str, 
                transaction_hour: int, transaction_day: int, age: int,
                city: str, city_pop: int = None, transaction_month: int = None) -> Dict:
        """
        Dự đoán fraud cho giao dịch (theo logic predict.py)
        
        Args:
            amt: Số tiền VND (REQUIRED)
            gender: Giới tính (Nam/Nữ) (REQUIRED)
            category: Loại giao dịch (Tiếng Việt) (REQUIRED)
            transaction_hour: Giờ 0-23 (REQUIRED)
            transaction_day: Ngày 0-6, Monday=0 (REQUIRED)
            age: Tuổi 18-100 (REQUIRED)
            city: Thành phố/Tỉnh VN (REQUIRED)
            city_pop: Dân số tỉnh/thành (OPTIONAL - nếu không có, tự lookup từ city)
            transaction_month: Tháng 1-12 (OPTIONAL)
            
        Returns:
            Dict chứa kết quả dự đoán
        """
        # Nếu không có city_pop, tự lookup từ city
        if city_pop is None:
            city_pop = self.lookup_city_population(city)
        
        # Prepare input
        X, converted = self.prepare_input_dataframe(
            amt, gender, category, transaction_hour, 
            transaction_day, age, city, city_pop, transaction_month
        )
        
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
