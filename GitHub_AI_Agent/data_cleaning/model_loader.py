import os
import joblib
import numpy as np
import logging
from catboost import CatBoostClassifier

MODEL_FILE = "models/catboost_outlier_model.pkl"

def load_or_train_outlier_model():
    """Loads the CatBoost outlier model or trains a new one if not found."""
    if os.path.exists(MODEL_FILE):
        logging.info(f"Loading existing CatBoost model from {MODEL_FILE}")
        return joblib.load(MODEL_FILE)
    else:
        logging.info("Training new CatBoost outlier model...")
        X_train = np.random.randn(1000, 5)
        y_train = np.random.choice([1, -1], size=1000, p=[0.95, 0.05])
        
        model = CatBoostClassifier(
            iterations=100, depth=6, learning_rate=0.1, loss_function='Logloss', verbose=False
        )
        model.fit(X_train, y_train)
        
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, MODEL_FILE)
        logging.info(f"Model saved to {MODEL_FILE}")
        return model

# Load model when module is imported
catboost_model = load_or_train_outlier_model()