import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import logging
import os
import json
from typing import Optional, Any

class RentalPricePredictor:
    def __init__(self) -> None:
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2
        )
        self.is_trained = False
        # relative to the CWD of the main.py script:
        self.model_path = 'models/saved_data/rent_predictor_model.joblib'
        self.metrics_path = 'models/saved_data/model_metrics.json'
        self.logger = logging.getLogger(__name__)
        self.metrics = {}
        self.feature_names = []
        
    def train(self, X: np.ndarray, y: np.ndarray, feature_names: list[str] | None = None) -> bool:
        """Train the rental price prediction model"""
        try:
            # Store feature names
            if feature_names:
                self.feature_names = feature_names.copy()
            
            # Split data for training and validation
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train the model
            self.model.fit(X_train, y_train)
            
            # Make predictions on test set
            y_pred = self.model.predict(X_test)
            
            # Calculate metrics
            self.metrics = {
                'mae': float(mean_absolute_error(y_test, y_pred)),
                'mse': float(mean_squared_error(y_test, y_pred)),
                'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
                'r2': float(r2_score(y_test, y_pred)),
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
            self.is_trained = True
            self.logger.info(f"Model trained successfully. R² Score: {self.metrics['r2']:.4f}")
            self.logger.info(f"Mean Absolute Error: €{self.metrics['mae']:.2f}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error training model: {str(e)}")
            return False
    
    def predict(self, features: np.ndarray) -> float:
        """Make a price prediction"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first or load_model().")
        
        try:
            prediction = self.model.predict(features)
            # Ensure prediction is positive and within reasonable bounds
            prediction = max(500, min(20000, prediction[0]))
            return float(prediction)
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {str(e)}")
            raise
    
    def get_feature_importance(self) -> dict[str, float]:
        """Get feature importance scores"""
        if not self.is_trained:
            return {}
        
        importance = self.model.feature_importances_
        
        if self.feature_names and len(self.feature_names) == len(importance):
            feature_importance = dict(zip(self.feature_names, importance))
        else:
            # Fallback to generic names
            feature_importance = {f"feature_{i}": float(importance[i]) for i in range(len(importance))}
        
        # Sort by importance
        return dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
    
    def save_model(self) -> None:
        """Save the trained model to disk"""
        if not self.is_trained:
            raise ValueError("Model not trained yet.")
        
        try:
            # Ensure models directory exists
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            
            # Save model
            model_data = {
                'model': self.model,
                'is_trained': self.is_trained,
                'feature_names': self.feature_names
            }
            joblib.dump(model_data, self.model_path)
            
            # Save metrics separately
            with open(self.metrics_path, 'w') as f:
                json.dump(self.metrics, f, indent=2)
            
            self.logger.info(f"Model saved to {self.model_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving model: {str(e)}")
            raise
    
    def load_model(self) -> bool:
        """Load a trained model from disk"""
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file {self.model_path} not found")
            
            # Load model
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.is_trained = model_data.get('is_trained', True)
            self.feature_names = model_data.get('feature_names', [])
            
            # Load metrics if available
            if os.path.exists(self.metrics_path):
                with open(self.metrics_path, 'r') as f:
                    self.metrics = json.load(f)
            
            self.logger.info(f"Model loaded from {self.model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading model: {str(e)}")
            raise
    
    def get_metrics(self) -> dict[str, Any]:
        """Get model performance metrics"""
        return self.metrics.copy() if self.metrics else {}
    
    def model_exists(self) -> bool:
        """Check if a saved model exists"""
        return os.path.exists(self.model_path)
