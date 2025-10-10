"""Model services providing fraud prediction helpers."""
import os
import json
import hashlib
import pandas as pd
import warnings
from flask import current_app


class ModelService:
    """Service class for ML model operations"""
    
    _model = None
    _config = None
    _test_dataset = None
    _amount_cache = {}  # Cache để đảm bảo deterministic matching
    
    @classmethod
    def load_model(cls):
        """Load the ML model and config from disk"""
        # Suppress XGBoost GPU warnings
        warnings.filterwarnings('ignore', message='.*gpu_hist.*')
        warnings.filterwarnings('ignore', message='.*mismatched devices.*')
        warnings.filterwarnings('ignore', category=UserWarning, module='xgboost')
        
        if cls._model is None:
            # Load model
            model_path = os.path.join('models', 'fraud_model_v2_flexible.pkl')
            config_path = os.path.join('models', 'fraud_config_v2_flexible.json')
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Config file not found: {config_path}")
            
            # Import EnsembleModel class before unpickling
            import sys
            try:
                from app.blueprints.model.ensemble import EnsembleModel as EnsembleModelClass

                # Ensure legacy module name works for pickled objects
                sys.modules.setdefault('EnsembleModel', type(sys)('EnsembleModel'))
                sys.modules['EnsembleModel'].EnsembleModel = EnsembleModelClass

                import __main__
                __main__.EnsembleModel = EnsembleModelClass

                current_app.logger.info("EnsembleModel class registered successfully")
            except ImportError as exc:
                current_app.logger.warning(f"Could not import EnsembleModel: {exc}")
            
            # Load model using joblib (more robust than pickle)
            try:
                import joblib
                model_dict = joblib.load(model_path)
                current_app.logger.info(f"Model loaded successfully with joblib from {model_path}")
                
                # Extract actual model from dictionary
                if isinstance(model_dict, dict):
                    if 'model' in model_dict:
                        cls._model = model_dict['model']
                        current_app.logger.info(f"Extracted model from dict: {type(cls._model).__name__}")
                    else:
                        cls._model = model_dict
                        current_app.logger.warning("Model dict doesn't have 'model' key, using whole dict")
                else:
                    cls._model = model_dict
                    current_app.logger.info(f"Model is not a dict: {type(cls._model).__name__}")
                
                # Force all XGBoost models to use CPU
                try:
                    if hasattr(cls._model, 'base_models'):
                        for i, base_model in enumerate(cls._model.base_models):
                            if hasattr(base_model, 'set_params'):
                                # XGBoost model - force CPU
                                base_model.set_params(device='cpu')
                                current_app.logger.info(f"Base model {i} set to use CPU")
                except Exception as e:
                    current_app.logger.warning(f"Could not set CPU device for base models: {e}")
                
            except Exception as e:
                current_app.logger.error(f"Error loading model: {str(e)}")
                raise
            
            with open(config_path, 'r') as f:
                cls._config = json.load(f)
            
            current_app.logger.info(f"Config loaded: {cls._config.get('n_selected_features')} features selected")
        
        return cls._model, cls._config
    
    @classmethod
    def load_test_dataset(cls):
        """Load creditcard_test_set.csv"""
        if cls._test_dataset is None:
            test_path = 'creditcard_test_set.csv'
            
            if not os.path.exists(test_path):
                raise FileNotFoundError(f"Test dataset not found: {test_path}")
            
            cls._test_dataset = pd.read_csv(test_path)
            current_app.logger.info(f"Test dataset loaded: {len(cls._test_dataset)} rows")
        
        return cls._test_dataset
    
    @classmethod
    def reload_model(cls):
        """Force reload the model"""
        cls._model = None
        cls._config = None
        cls._test_dataset = None
        cls._amount_cache = {}
        return cls.load_model()
    
    @classmethod
    def find_matching_row(cls, amount_usd: float) -> dict:
        """
        Find matching row in test dataset based on amount (deterministic)
        
        Sử dụng hash của amount để luôn trả về cùng row cho cùng amount
        
        Args:
            amount_usd: Transaction amount in USD
            
        Returns:
            dict: Matched row data
        """
        df = cls.load_test_dataset()
        
        # Tạo cache key từ amount (làm tròn 2 số thập phân)
        cache_key = round(amount_usd, 2)
        
        # Kiểm tra cache
        if cache_key in cls._amount_cache:
            row_idx = cls._amount_cache[cache_key]
            current_app.logger.info(f"Using cached match for amount ${cache_key}: row {row_idx}")
            return df.iloc[row_idx].to_dict()
        
        # IMPORTANT: Create a COPY to avoid modifying shared DataFrame
        df_copy = df.copy()
        
        # Tìm rows có Amount gần giống nhất
        df_copy['amount_diff'] = abs(df_copy['Amount'] - amount_usd)
        closest_rows = df_copy.nsmallest(10, 'amount_diff')  # Lấy 10 rows gần nhất
        
        # Sử dụng hash để chọn deterministic
        # Hash amount -> số nguyên -> chọn index trong 10 rows
        hash_value = int(hashlib.md5(str(cache_key).encode()).hexdigest(), 16)
        selected_idx = hash_value % len(closest_rows)
        
        matched_row = closest_rows.iloc[selected_idx]
        row_idx = matched_row.name  # Original index in dataframe
        
        # Cache kết quả
        cls._amount_cache[cache_key] = row_idx
        
        current_app.logger.info(
            f"Matched amount ${amount_usd:.2f} -> row {row_idx} "
            f"(Amount: ${matched_row['Amount']:.2f}, diff: ${matched_row['amount_diff']:.2f})"
        )
        
        # Remove temporary column
        result = matched_row.drop('amount_diff').to_dict()
        
        return result
    
    @classmethod
    def predict_from_amount(cls, amount_usd: float) -> dict:
        """
        Predict fraud based on transaction amount
        
        Args:
            amount_usd: Transaction amount in USD
            
        Returns:
            dict: Prediction result with matched transaction data
        """
        try:
            current_app.logger.info(f"[SERVICE] predict_from_amount START: amount=${amount_usd}")
            
            model, config = cls.load_model()
            current_app.logger.info("[SERVICE] Model and config loaded")
            
            # Find matching row
            matched_row = cls.find_matching_row(amount_usd)
            current_app.logger.info(f"[SERVICE] Matched row found: {len(matched_row)} fields")
            
            # Get selected features from config
            selected_features = config.get('selected_features', [])
            
            if not selected_features:
                raise ValueError("No selected features found in config")
            
            # Prepare features
            feature_values = []
            for feat in selected_features:
                if feat in matched_row:
                    feature_values.append(matched_row[feat])
                elif feat == 'hour_of_day':
                    # Calculate hour_of_day from Time (seconds since first transaction)
                    time_seconds = matched_row.get('Time', 0)
                    hour = int((time_seconds % 86400) / 3600)  # 86400 seconds in a day
                    feature_values.append(hour)
                    current_app.logger.debug(f"Calculated hour_of_day={hour} from Time={time_seconds}")
                else:
                    current_app.logger.warning(f"Feature {feat} not found in matched row, using 0")
                    feature_values.append(0.0)
            
            current_app.logger.info(f"[SERVICE] Feature values prepared: {len(feature_values)} features")
            
            X_input = pd.DataFrame([feature_values], columns=selected_features)
            current_app.logger.info("[SERVICE] DataFrame created")
            current_app.logger.info(f"[SERVICE] X_input shape: {X_input.shape}, dtype: {X_input.dtypes.tolist()}")
            
            # Make prediction
            current_app.logger.info("=" * 80)
            current_app.logger.info("[PREDICTION] ABOUT TO CALL model.predict_proba()")
            current_app.logger.info(f"[PREDICTION] Model type: {type(model).__name__}")
            current_app.logger.info(f"[PREDICTION] Input shape: {X_input.shape}")
            current_app.logger.info("=" * 80)
            
            try:
                fraud_proba = model.predict_proba(X_input)[0, 1]  # Probability of fraud (class 1)
                
                current_app.logger.info("=" * 80)
                current_app.logger.info("[PREDICTION] model.predict_proba() COMPLETED SUCCESSFULLY")
                current_app.logger.info(f"[PREDICTION] Result: fraud_proba={fraud_proba}")
                current_app.logger.info("=" * 80)
                
            except Exception as predict_error:
                current_app.logger.error("=" * 80)
                current_app.logger.error("[PREDICTION] ERROR IN model.predict_proba()")
                current_app.logger.error(f"[PREDICTION] Error type: {type(predict_error).__name__}")
                current_app.logger.error(f"[PREDICTION] Error message: {str(predict_error)}")
                current_app.logger.error("=" * 80)
                import traceback
                current_app.logger.error(traceback.format_exc())
                raise
            
            current_app.logger.info(f"[SERVICE] Prediction completed: fraud_proba={fraud_proba}")
            
            # Get threshold from config
            threshold = config.get('chosen_threshold', 0.5)
            is_fraud = fraud_proba >= threshold
            
            # Determine confidence and risk level
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
                confidence = "high"
            else:
                risk_level = "very_high"
                confidence = "very_high"
            
            current_app.logger.info("[SERVICE] Building result dictionary")
            
            try:
                result = {
                    'success': True,
                    'amount_usd': float(amount_usd),
                    'matched_transaction': {
                        'amount': float(matched_row.get('Amount', 0)),
                        'time': float(matched_row.get('Time', 0)),
                        'actual_label': int(matched_row.get('Class', 0)),  # 0 = legitimate, 1 = fraud
                    },
                    'prediction': {
                        'is_fraud': bool(is_fraud),
                        'fraud_probability': float(fraud_proba),
                        'confidence': confidence,
                        'risk_level': risk_level,
                        'threshold_used': float(threshold)
                    },
                    'features_used': selected_features,
                    'model_version': 'v2_flexible',
                    'model_metrics': {
                        'pr_auc': config.get('metrics', {}).get('pr_auc', 0),
                        'roc_auc': config.get('metrics', {}).get('roc_auc', 0),
                        'f1': config.get('metrics', {}).get('f1', 0)
                    }
                }
                current_app.logger.info("[SERVICE] Result dictionary built successfully")
                
            except Exception as build_error:
                current_app.logger.error(f"[SERVICE] ERROR building result dictionary: {build_error}")
                import traceback
                current_app.logger.error(traceback.format_exc())
                raise
            
            current_app.logger.info(
                f"Prediction for ${amount_usd}: "
                f"fraud_prob={fraud_proba:.4f}, is_fraud={is_fraud}, risk={risk_level}"
            )
            
            current_app.logger.info("=" * 80)
            current_app.logger.info("[SERVICE] predict_from_amount COMPLETE - ABOUT TO RETURN")
            current_app.logger.info(f"[SERVICE] Returning dict with {len(result)} keys")
            current_app.logger.info("=" * 80)
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"[SERVICE] Exception in predict_from_amount: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())
            raise
    
