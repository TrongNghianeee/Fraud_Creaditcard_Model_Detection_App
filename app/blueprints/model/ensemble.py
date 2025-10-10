"""Ensemble model utilities for unpickling stacking models."""
import numpy as np


class EnsembleModel:
    """Stacking ensemble model wrapper compatible with persisted models."""

    def __init__(self, base_models=None, meta_model=None, use_stacking=True):
        self.base_models = base_models or []
        self.meta_model = meta_model
        self.use_stacking = use_stacking
        self.is_fitted = False

    def predict(self, X):
        """Return hard class predictions based on meta-model probabilities."""
        proba = self.predict_proba(X)
        return (proba[:, 1] >= 0.5).astype(int)

    def predict_proba(self, X):
        """Return stacked ensemble probabilities for each class."""
        if not self.use_stacking or not self.base_models or not self.meta_model:
            raise NotImplementedError("Model not properly configured for stacking")

        base_predictions = []
        for base_model in self.base_models:
            predictions = base_model.predict_proba(X)
            base_predictions.append(predictions[:, 1])

        X_meta = np.column_stack(base_predictions)
        return self.meta_model.predict_proba(X_meta)
