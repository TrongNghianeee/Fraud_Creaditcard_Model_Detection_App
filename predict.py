"""
FRAUD DETECTION PREDICTION SCRIPT - DEMO VERSION
Sử dụng model fraud_detection_fa_smoteenn.pkl để dự đoán giao dịch gian lận

DEMO INPUT FIELDS (VN format):
✅ amt              → Số tiền (VND, sẽ convert sang USD) [REQUIRED]
✅ gender           → Giới tính (nam/nữ) [REQUIRED]
✅ category         → Loại giao dịch (Tiếng Việt: du lịch, ăn uống, etc.) [REQUIRED]
✅ transaction_hour → Giờ giao dịch (0-23) [REQUIRED]
✅ transaction_day  → Ngày trong tuần (0-6, Mon=0, Sun=6) [REQUIRED]
✅ age              → Tuổi (18-100) [REQUIRED]
✅ city             → Thành phố/Tỉnh (chọn từ 63 tỉnh thành VN, sẽ map sang city_pop) [REQUIRED]
⭕ transaction_month→ Tháng (1-12, optional, default=6)

Note: Model sử dụng FA-selected features, các features khác (job, merchant, lat/long) 
      được set về giá trị default từ training data.
"""

import pandas as pd
import numpy as np
import joblib
import warnings
import json
from datetime import datetime
from typing import Dict, Union, List
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
    # PHẢI KHỚP VỚI TRAINING CONFIG
    selection_ratio: float = 0.6
    min_feature_ratio: float = 0.5
    max_feature_ratio: float = 0.7
    min_feature_count: int = 10
    random_state: int = 42
    feature_selection_mode: str = "random"
    n_fireflies: int = 40
    n_epochs: int = 10
    alpha: float = 0.25
    beta0: float = 2.0
    gamma: float = 0.20
    lambda_feat: float = 0.01
    diversity_threshold: float = 0.1
    patience: int = 4
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
        X['trans_date_trans_time'] = pd.to_datetime(X['trans_date_trans_time'])
        X['dob'] = pd.to_datetime(X['dob'])
        X['transaction_hour'] = X['trans_date_trans_time'].dt.hour
        X['transaction_day'] = X['trans_date_trans_time'].dt.dayofweek
        X['transaction_month'] = X['trans_date_trans_time'].dt.month
        X['age'] = (X['trans_date_trans_time'] - X['dob']).dt.days // 365
        X.drop(['trans_date_trans_time', 'dob', 'unix_time'], axis=1, inplace=True, errors='ignore')
        return X


class CategoricalEncoder(BaseEstimator, TransformerMixin):
    """Encode categorical features"""
    
    def __init__(self):
        self.label_encoders = {}
    
    def fit(self, X, y=None):
        X = X.copy()
        cat_cols = X.select_dtypes(include=['object']).columns.tolist()
        for col in cat_cols:
            le = LabelEncoder()
            X[col] = X[col].fillna('unknown')
            le.fit(X[col].astype(str))
            self.label_encoders[col] = le
        return self
    
    def transform(self, X):
        X = X.copy()
        for col, le in self.label_encoders.items():
            if col in X.columns:
                X[col] = X[col].fillna(le.classes_[0])
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
        num_cols = X.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            self.fill_values[col] = X[col].median()
        return self
    
    def transform(self, X):
        X = X.copy()
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
# Source: approximate 2020 population estimates (rounded)
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

# Feature name mapping (after preprocessing pipeline transforms)
# Raw features → Processed feature indices:
# After DateFeatureExtractor, CategoricalEncoder, Scaler:
# feature_0: cc_num, feature_1: merchant, feature_2: category, feature_3: amt
# feature_4: first, feature_5: last, feature_6: gender, feature_7: street
# feature_8: city, feature_9: state, feature_10: zip, feature_11: lat
# feature_12: long, feature_13: city_pop, feature_14: job, feature_15: merch_lat
# feature_16: merch_long, feature_17: transaction_hour, feature_18: transaction_day
# feature_19: transaction_month, feature_20: age

FEATURE_INDEX_TO_NAME = {
    0: 'cc_num', 1: 'merchant', 2: 'category', 3: 'amt',
    4: 'first', 5: 'last', 6: 'gender', 7: 'street',
    8: 'city', 9: 'state', 10: 'zip', 11: 'lat',
    12: 'long', 13: 'city_pop', 14: 'job', 15: 'merch_lat',
    16: 'merch_long', 17: 'transaction_hour', 18: 'transaction_day',
    19: 'transaction_month', 20: 'age'
}

# Top 15 features from FA training (with importances)
# Mapped from feature_X to actual feature names
TOP_FEATURES = [
    {"feature": "amt", "importance": 0.5598474144935608},           # feature_3
    {"feature": "transaction_hour", "importance": 0.1695917546749115},  # feature_17
    {"feature": "category", "importance": 0.11849434673786163},     # feature_2
    {"feature": "gender", "importance": 0.024299195036292076},      # feature_6
    {"feature": "transaction_day", "importance": 0.023388203233480453},  # feature_18
    {"feature": "cc_num", "importance": 0.01652321219444275},       # feature_0
    {"feature": "age", "importance": 0.01585434004664421},          # feature_20
    {"feature": "job", "importance": 0.01144478190690279},          # feature_14
    {"feature": "city_pop", "importance": 0.011324348859488964},    # feature_13
    {"feature": "lat", "importance": 0.009946261532604694},         # feature_11
    {"feature": "first", "importance": 0.008818736299872398},       # feature_4
    {"feature": "long", "importance": 0.00842238124459982},         # feature_12
    {"feature": "last", "importance": 0.00819438323378563},         # feature_5
    {"feature": "city", "importance": 0.008027640171349049},        # feature_8
    {"feature": "merch_lat", "importance": 0.0058229463174939156}   # feature_15
]


def convert_vnd_to_usd(vnd_amount: float) -> float:
    return vnd_amount / VND_TO_USD_RATE


def convert_category(category_input: str) -> str:
    category_lower = category_input.lower().strip()
    if category_lower in CATEGORY_VN_TO_EN:
        return CATEGORY_VN_TO_EN[category_lower]
    all_en_categories = list(CATEGORY_VN_TO_EN.values())
    if category_lower in [c.lower() for c in all_en_categories]:
        return category_lower
    raise ValueError(f"Category '{category_input}' không hợp lệ.")


def convert_gender(gender_input: str) -> str:
    gender_lower = gender_input.lower().strip()
    if gender_lower in GENDER_VN_TO_EN:
        return GENDER_VN_TO_EN[gender_lower]
    if gender_lower in ['m', 'f']:
        return gender_lower.upper()
    raise ValueError(f"Gender '{gender_input}' không hợp lệ.")


def lookup_city_population(city_input: str) -> int:
    city_lower = city_input.lower().strip()
    return PROVINCE_POPULATION.get(city_lower, 1000000)


def normalize_hour(hour: int) -> int:
    return max(0, min(23, int(hour)))


def normalize_day(day: int) -> int:
    return max(0, min(6, int(day)))


def normalize_month(month: int) -> int:
    return max(1, min(12, int(month)))


def normalize_age(age: int) -> int:
    return max(18, min(100, int(age)))


# ============================================================================
# FRAUD DETECTION PIPELINE WRAPPER (Required for unpickling saved model)
# ============================================================================

class FraudDetectionPipeline:
    """
    Complete fraud detection pipeline wrapper
    Combines preprocessing + classifier + optimal threshold
    This class is required to unpickle the saved model
    """
    def __init__(self, preprocessor, classifier, threshold=0.5):
        self.preprocessor = preprocessor
        self.classifier = classifier
        self.threshold = threshold
    
    def predict_proba(self, X):
        """Predict probability for fraud class"""
        X_processed = self.preprocessor.transform(X)
        return self.classifier.predict_proba(X_processed)
    
    def predict(self, X):
        """Predict fraud class with optimal threshold"""
        proba = self.predict_proba(X)[:, 1]
        return (proba >= self.threshold).astype(int)
    
    def get_params(self):
        """Get pipeline parameters"""
        return {
            'threshold': self.threshold,
            'classifier_params': self.classifier.get_params(),
            'preprocessor_steps': list(self.preprocessor.named_steps.keys())
        }


# ============================================================================
# FRAUD DETECTOR CLASS
# ============================================================================

class FraudDetector:
    def __init__(self, model_path='fraud_detection_fa_smoteenn.pkl'):
        print(f"Loading FA model from {model_path}...")
        self.pipeline = joblib.load(model_path)
        print("✅ FA Model loaded successfully!")
        # Default values cho các fields KHÔNG required (sẽ dùng giá trị phổ biến từ training data)
        self.default_values = {
            'merchant': 'fraud_Kirlin and Sons',
            'street': 'Main St',
            'city': 'Houston',  # US city (cho pipeline, khác với VN city input)
            'state': 'TX',
            'zip': 77001,
            'job': 'Food service',
            'lat': 29.7604,
            'long': -95.3698,
            'merch_lat': 29.7604,
            'merch_long': -95.3698,
            'transaction_month': 6  # Default month nếu không cung cấp
        }
    
    def prepare_input(self, user_input: Dict) -> pd.DataFrame:
        # Required fields - BẮT BUỘC phải cung cấp
        required = ['category', 'amt', 'gender', 'transaction_hour', 'transaction_day', 'age', 'city']
        for field in required:
            if field not in user_input:
                raise ValueError(f"Missing required field: {field}")
        
        # Convert & validate required fields
        category_en = convert_category(user_input['category'])
        vnd_amount = float(user_input['amt'])
        if vnd_amount <= 0:
            raise ValueError(f"Amount must be > 0")
        amt_usd = convert_vnd_to_usd(vnd_amount)
        gender = convert_gender(user_input['gender'])
        transaction_hour = normalize_hour(user_input['transaction_hour'])
        transaction_day = normalize_day(user_input['transaction_day'])
        age = normalize_age(user_input['age'])
        city_input = user_input['city']
        city_pop = lookup_city_population(city_input)
        
        # Optional field with default
        transaction_month = normalize_month(user_input.get('transaction_month', self.default_values['transaction_month']))
        
        now = datetime.now()
        transaction_date = now.replace(hour=transaction_hour, minute=0, second=0, microsecond=0, day=1, month=transaction_month)
        dob = datetime(now.year - age, now.month, now.day)
        
        data = {
            'cc_num': 1234567890123456, 'merchant': self.default_values['merchant'],
            'category': category_en, 'amt': amt_usd, 'first': 'John', 'last': 'Doe',
            'gender': gender, 'street': self.default_values['street'],
            'city': self.default_values['city'], 'state': self.default_values['state'],
            'zip': self.default_values['zip'], 'lat': self.default_values['lat'],
            'long': self.default_values['long'], 'city_pop': city_pop,
            'job': self.default_values['job'], 'merch_lat': self.default_values['merch_lat'],
            'merch_long': self.default_values['merch_long'],
            'trans_date_trans_time': transaction_date, 'dob': dob
        }
        
        self._last_input = {
            'category_vn': user_input['category'], 'category_en': category_en,
            'amt_vnd': vnd_amount, 'amt_usd': amt_usd,
            'gender_vn': user_input.get('gender', ''), 'gender_en': gender,
            'transaction_hour': transaction_hour, 'transaction_day': transaction_day,
            'transaction_month': transaction_month, 'age': age,
            'city': city_input, 'city_pop': city_pop
        }
        
        return pd.DataFrame([data])
    
    def predict(self, user_input: Dict, return_explanation=True) -> Dict:
        X = self.prepare_input(user_input)
        proba = self.pipeline.predict_proba(X)[0]
        prediction = self.pipeline.predict(X)[0]
        
        result = {
            'is_fraud': bool(prediction),
            'fraud_probability': float(proba[1]),
            'safe_probability': float(proba[0]),
            'prediction_class': int(prediction),
            'input_summary': {
                'category': f"{self._last_input['category_vn']} ({self._last_input['category_en']})",
                'amount': f"{self._last_input['amt_vnd']:,.0f} VND (${self._last_input['amt_usd']:.2f} USD)",
                'gender': f"{self._last_input['gender_vn']} ({self._last_input['gender_en']})",
                'transaction_hour': f"{self._last_input['transaction_hour']:02d}:00",
                'transaction_day': self._last_input['transaction_day'],
                'transaction_month': self._last_input['transaction_month'],
                'age': self._last_input['age'],
                'city': self._last_input['city'],
                'city_pop': f"{self._last_input['city_pop']:,}"
            }
        }
        
        if return_explanation:
            result['explanation'] = {
                'message': 'Top 15 features influencing this prediction (from FA feature selection):',
                'top_features': TOP_FEATURES,  # All 15 features
                'all_features_count': len(TOP_FEATURES),
                'note': 'FA selected 15 out of 21 total features after preprocessing'
            }
        
        self._print_result(result)
        return result
    
    def _print_result(self, result: Dict):
        print("\n" + "="*70)
        print(" FRAUD DETECTION - PREDICTION RESULT ")
        print("="*70)
        print("\n[INPUT SUMMARY]")
        for key, val in result['input_summary'].items():
            print(f"  {key:20s}: {val}")
        print("\n[PREDICTION]")
        if result['is_fraud']:
            print(f"  ⚠️  FRAUD DETECTED!")
            print(f"  🚨 Fraud Probability: {result['fraud_probability']*100:.2f}%")
        else:
            print(f"  ✅ LEGITIMATE TRANSACTION")
            print(f"  ✓  Safe Probability: {result['safe_probability']*100:.2f}%")
        if 'explanation' in result:
            print("\n[EXPLANATION - Top 15 FA-Selected Features]")
            for i, feat in enumerate(result['explanation']['top_features'], 1):
                print(f"  {i:2d}. {feat['feature']:20s}: {feat['importance']:.6f}")
            print(f"\n  Note: {result['explanation']['note']}")
        print("="*70 + "\n")


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_demo():
    print("\n" + "="*80)
    print(" DEMO: FRAUD DETECTION WITH VN INPUT ")
    print("="*80 + "\n")
    detector = FraudDetector(model_path='fraud_detection_fa_smoteenn.pkl')
    transaction = {
        'category': 'xăng dầu', 'amt': 20000, 'gender': 'nữ',
        'transaction_hour': 22, 'transaction_day': 5,
        'age': 28, 'city': 'ha noi'
    }
    result = detector.predict(transaction)
    return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'demo':
        example_demo()
    else:
        print("Running default mode: single transaction demo")
        print("Use: python predict.py demo")
        example_demo()
