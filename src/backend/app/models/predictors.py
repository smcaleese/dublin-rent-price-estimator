import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import logging
import os
import json
from typing import Optional, Any
from abc import ABC, abstractmethod


class BasePricePredictor(ABC):
    """Abstract base class for price prediction models"""
    
    def __init__(self, model_path: str, metrics_path: str) -> None:
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2
        )
        self.is_trained = False
        self.model_path = model_path
        self.metrics_path = metrics_path
        self.logger = logging.getLogger(__name__)
        self.metrics = {}
        self.feature_names = []

    def train(self, X: np.ndarray, y: np.ndarray, feature_names: list[str] | None = None) -> bool:
        """Train the price prediction model"""
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
            model_type = self.__class__.__name__
            self.logger.info(f"{model_type} trained successfully. R² Score: {self.metrics['r2']:.4f}")
            self.logger.info(f"Mean Absolute Error: €{self.metrics['mae']:.2f}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error training model: {str(e)}")
            return False

    @abstractmethod
    def predict(self, features: np.ndarray) -> dict[str, float]:
        """Make a price prediction - to be implemented by subclasses"""
        pass

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
            
            model_type = self.__class__.__name__
            self.logger.info(f"{model_type} saved to {self.model_path}")
            
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
            
            model_type = self.__class__.__name__
            self.logger.info(f"{model_type} loaded from {self.model_path}")
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


class PropertyPricePredictor(BasePricePredictor):
    """Price predictor for whole property rentals"""
    
    def predict(self, features: np.ndarray) -> dict[str, float]:
        """Make a price prediction for whole properties, including a confidence interval."""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first or load_model().")
        
        try:
            # Get predictions from all trees in the forest
            # features is expected to be a 2D array for a single sample, e.g., [[f1, f2, ...]]
            # tree.predict(features) returns an array like [prediction_value]
            tree_predictions_raw = np.array([tree.predict(features) for tree in self.model.estimators_])
            
            # Flatten the array to get [pred_tree1, pred_tree2, ...]
            tree_predictions = tree_predictions_raw.flatten()

            point_estimate = float(np.mean(tree_predictions))
            lower_bound = float(np.percentile(tree_predictions, 5))  # 5th percentile for 90% CI
            upper_bound = float(np.percentile(tree_predictions, 95)) # 95th percentile for 90% CI

            # Apply clamping
            min_price, max_price = 500, 20000
            point_estimate_clamped = max(min_price, min(max_price, point_estimate))
            lower_bound_clamped = max(min_price, min(max_price, lower_bound))
            upper_bound_clamped = max(min_price, min(max_price, upper_bound))

            # Ensure lower_bound <= point_estimate <= upper_bound after clamping
            # Adjust bounds relative to the clamped point estimate if necessary
            final_lower_bound = min(lower_bound_clamped, point_estimate_clamped)
            final_upper_bound = max(upper_bound_clamped, point_estimate_clamped)
            
            # Further ensure lower is not greater than upper after all adjustments
            if final_lower_bound > final_upper_bound:
                # This case might happen if clamping severely distorts the interval.
                # Default to point_estimate for bounds or a small interval around it.
                final_lower_bound = final_upper_bound = point_estimate_clamped

            return {
                "prediction": point_estimate_clamped,
                "lower_bound": final_lower_bound,
                "upper_bound": final_upper_bound,
            }
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {str(e)}")
            raise


class SharedRoomPricePredictor(BasePricePredictor):
    """Price predictor for shared room rentals"""
    
    def predict(self, features: np.ndarray) -> dict[str, float]:
        """Make a price prediction for shared rooms, including a confidence interval."""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first or load_model().")
        
        try:
            # Get predictions from all trees in the forest
            tree_predictions_raw = np.array([tree.predict(features) for tree in self.model.estimators_])
            tree_predictions = tree_predictions_raw.flatten()

            point_estimate = float(np.mean(tree_predictions))
            lower_bound = float(np.percentile(tree_predictions, 5))  # 5th percentile
            upper_bound = float(np.percentile(tree_predictions, 95)) # 95th percentile

            # Apply clamping
            min_price, max_price = 200, 15000
            point_estimate_clamped = max(min_price, min(max_price, point_estimate))
            lower_bound_clamped = max(min_price, min(max_price, lower_bound))
            upper_bound_clamped = max(min_price, min(max_price, upper_bound))

            # Ensure lower_bound <= point_estimate <= upper_bound after clamping
            final_lower_bound = min(lower_bound_clamped, point_estimate_clamped)
            final_upper_bound = max(upper_bound_clamped, point_estimate_clamped)

            if final_lower_bound > final_upper_bound:
                final_lower_bound = final_upper_bound = point_estimate_clamped

            return {
                "prediction": point_estimate_clamped,
                "lower_bound": final_lower_bound,
                "upper_bound": final_upper_bound,
            }
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {str(e)}")
            raise
