import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import OneHotEncoder
import logging
import os
import joblib
import json
from typing import Optional, Any, Tuple
from abc import ABC, abstractmethod


class BaseDataProcessor(ABC):
    """Abstract base class for data processors"""
    
    def __init__(self) -> None:
        self.df = None
        self.prop_type_encoder = OneHotEncoder(
            sparse_output=False, handle_unknown="ignore"
        )
        self.dublin_area_encoder = OneHotEncoder(
            sparse_output=False, handle_unknown="ignore"
        )
        self.feature_names = None
        self.logger = logging.getLogger(__name__)

    def load_data(self, file_path: str) -> bool:
        """Load and clean the rental data"""
        try:
            self.df = pd.read_csv(file_path)
            self.logger.info(f"Loaded {len(self.df)} records from {file_path}")

            # Clean the data
            self._clean_data()

            self.logger.info(f"Cleaned data: {len(self.df)} records remaining")
            return True

        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            return False

    @abstractmethod
    def _clean_data(self) -> None:
        """Clean the training data - to be implemented by subclasses"""
        pass

    @abstractmethod
    def prepare_features(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features (X) and target (y) for model training - to be implemented by subclasses"""
        pass

    @abstractmethod
    def encode_input(self, input_data: dict) -> np.ndarray:
        """Encode user input for prediction - to be implemented by subclasses"""
        pass

    def _extract_dublin_postal_code(self, address_series: pd.Series) -> pd.Series:
        """Extract numeric Dublin postal codes from address strings"""

        def extract_code(address: Any) -> Any:
            if pd.isna(address):
                return np.nan

            # Convert to string and make uppercase for consistent matching
            address_str = str(address).upper()

            # Pattern 1: "Dublin X" where X is 1-2 digits
            match = re.search(r"DUBLIN\s+(\d{1,2})", address_str, flags=re.IGNORECASE)
            if match:
                return int(match.group(1))

            # Pattern 2: "DX" where X is 1-2 digits (e.g., D2, D15)
            match = re.search(r"\bD(\d{1,2})\b", address_str)
            if match:
                return int(match.group(1))

            # Pattern 3: "D0X" where X is a digit (e.g., D08)
            match = re.search(r"\bD0(\d)\b", address_str)
            if match:
                return int(match.group(1))

            return np.nan

        return address_series.apply(extract_code)

    def _extract_numeric_area_from_frontend(self, dublin_area_str: str) -> int:
        """Extract numeric area from frontend format"""
        if pd.isna(dublin_area_str):
            return 1  # Default fallback

        # Extract number from strings like "dublin-1", "dublin-15"
        match = re.search(r"dublin-(\d+)", str(dublin_area_str).lower())
        if match:
            return int(match.group(1))

        # If no match, try to extract any number
        match = re.search(r"(\d+)", str(dublin_area_str))
        if match:
            return int(match.group(1))

        return 1  # Default fallback

    def get_property_types(self) -> list[str]:
        """Get list of available property types"""
        if (
            hasattr(self.prop_type_encoder, "categories_")
            and len(self.prop_type_encoder.categories_) > 0
        ):
            return self.prop_type_encoder.categories_[0].tolist()
        return ["Apartment", "House", "Studio"]

    def get_dublin_areas(self) -> list[int]:
        """Get list of available Dublin areas"""
        if (
            hasattr(self.dublin_area_encoder, "categories_")
            and len(self.dublin_area_encoder.categories_) > 0
        ):
            return sorted(
                [int(area) for area in self.dublin_area_encoder.categories_[0]]
            )
        return []

    def get_data_summary(self) -> dict[str, Any]:
        """Get summary statistics of the data"""
        if self.df is None:
            return {}

        if self.df.empty:
            return {
                "total_records": 0,
                "median_price": 0,
                "min_price": 0,
                "max_price": 0,
                "property_types": {},
                "dublin_areas": {},
                "message": "No data available."
            }

        return {
            "total_records": len(self.df),
            "median_price": float(self.df["price"].median()) if not self.df["price"].empty else 0,
            "min_price": float(self.df["price"].min()) if not self.df["price"].empty else 0,
            "max_price": float(self.df["price"].max()) if not self.df["price"].empty else 0,
            "property_types": self.df["prop_type"].value_counts().to_dict(),
            "dublin_areas": self.df["dublin_area"].value_counts().to_dict(),
        }

    def get_feature_names(self) -> list[str]:
        """Get the feature names after encoding"""
        return self.feature_names.copy() if self.feature_names else []
    
    def save_encoders(self, path_prefix: str) -> None:
        """Save the fitted encoders to disk"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(path_prefix), exist_ok=True)
            
            # Save common encoders
            joblib.dump(self.prop_type_encoder, f"{path_prefix}prop_type_encoder.joblib")
            joblib.dump(self.dublin_area_encoder, f"{path_prefix}dublin_area_encoder.joblib")
            
            # Save additional encoders if they exist (implemented in subclasses)
            self._save_additional_encoders(path_prefix)
            
            # Save feature names
            if self.feature_names:
                with open(f"{path_prefix}feature_names.json", 'w') as f:
                    json.dump(self.feature_names, f)
            
            self.logger.info(f"Encoders saved with prefix: {path_prefix}")
            
        except Exception as e:
            self.logger.error(f"Error saving encoders: {str(e)}")
            raise
    
    def load_encoders(self, path_prefix: str) -> None:
        """Load the fitted encoders from disk"""
        try:
            # Load common encoders
            self.prop_type_encoder = joblib.load(f"{path_prefix}prop_type_encoder.joblib")
            self.dublin_area_encoder = joblib.load(f"{path_prefix}dublin_area_encoder.joblib")
            
            # Load additional encoders if they exist (implemented in subclasses)
            self._load_additional_encoders(path_prefix)
            
            # Load feature names
            feature_names_path = f"{path_prefix}feature_names.json"
            if os.path.exists(feature_names_path):
                with open(feature_names_path, 'r') as f:
                    self.feature_names = json.load(f)
            
            self.logger.info(f"Encoders loaded with prefix: {path_prefix}")
            
        except Exception as e:
            self.logger.error(f"Error loading encoders: {str(e)}")
            raise

    def _save_additional_encoders(self, path_prefix: str) -> None:
        """Save additional encoders specific to subclass - override in subclasses if needed"""
        pass

    def _load_additional_encoders(self, path_prefix: str) -> None:
        """Load additional encoders specific to subclass - override in subclasses if needed"""
        pass


class PropertyDataProcessor(BaseDataProcessor):
    """Data processor for whole property rentals"""
    
    def _clean_data(self) -> None:
        """Clean the training data by handling missing values and converting data types"""
        if self.df is None:
            raise ValueError("Data not loaded")

        # Handle 'N/A' strings in price column
        self.df["price"] = self.df["price"].replace("N/A", np.nan)

        # Convert price to numeric
        self.df["price"] = pd.to_numeric(self.df["price"], errors="coerce")
        
        # Property model: beds, baths, prop_type, address
        self.df["beds"] = pd.to_numeric(self.df["beds"], errors="coerce")
        self.df["baths"] = pd.to_numeric(self.df["baths"], errors="coerce")
        
        # Extract Dublin postal codes from address
        self.df["dublin_area"] = self._extract_dublin_postal_code(self.df["address"])
        
        # Drop rows with missing essential data for property model
        essential_columns = ["price", "beds", "baths", "prop_type", "dublin_area"]
        self.df = self.df.dropna(subset=essential_columns)

        # Filter out unrealistic prices (less than 200 or greater than 20000)
        self.df = self.df[(self.df["price"] >= 200) & (self.df["price"] <= 20000)]

    def prepare_features(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features (X) and target (y) for model training"""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        # Fit and transform categorical features
        prop_type_encoded = self.prop_type_encoder.fit_transform(self.df[["prop_type"]])
        dublin_area_encoded = self.dublin_area_encoder.fit_transform(
            self.df[["dublin_area"]]
        )

        # Create feature names for categorical features
        prop_type_features = [
            f"prop_type_{cat}" for cat in self.prop_type_encoder.categories_[0]
        ]
        dublin_area_features = [
            f"dublin_area_{int(cat)}" for cat in self.dublin_area_encoder.categories_[0]
        ]

        # Property model: beds, baths, prop_type (one-hot), address (one-hot)
        numeric_features = ["beds", "baths"]
        X_numeric = self.df[numeric_features].values
        
        # Combine all features
        X = np.hstack([X_numeric, prop_type_encoded, dublin_area_encoded])
        
        # Store feature names
        self.feature_names = (
            numeric_features + prop_type_features + dublin_area_features
        )

        # Target
        y = self.df["price"].values

        self.logger.info(f"Prepared features: {X.shape}")
        self.logger.info(f"Feature names: {self.feature_names}")

        return X, y

    def encode_input(self, input_data: dict) -> np.ndarray:
        """Encode user input for prediction"""
        try:
            # Extract numeric Dublin area from frontend format (e.g., "dublin-1" -> 1)
            dublin_area_numeric = self._extract_numeric_area_from_frontend(input_data.get("address", ""))

            # Prepare data for encoding categorical features
            prop_type_df = pd.DataFrame({"prop_type": [input_data.get("property_type", "")]})
            dublin_area_df = pd.DataFrame({"dublin_area": [dublin_area_numeric]})

            # Transform using fitted encoders
            prop_type_encoded = self.prop_type_encoder.transform(prop_type_df)
            dublin_area_encoded = self.dublin_area_encoder.transform(dublin_area_df)

            # Property model: beds, baths, prop_type (one-hot), address (one-hot)
            beds = pd.to_numeric(input_data.get("bedrooms", 1), errors="coerce")
            baths = pd.to_numeric(input_data.get("bathrooms", 1), errors="coerce")
            
            # Handle NaN values with defaults
            if pd.isna(beds):
                beds = 1
            if pd.isna(baths):
                baths = 1
            
            # Combine features in the same order as prepare_features
            X_numeric = np.array([[beds, baths]])
            X = np.hstack([X_numeric, prop_type_encoded, dublin_area_encoded])

            return X

        except Exception as e:
            self.logger.error(f"Error encoding input: {str(e)}")
            raise


class SharedRoomDataProcessor(BaseDataProcessor):
    """Data processor for shared room rentals"""
    
    def __init__(self) -> None:
        super().__init__()
        self.room_type_encoder = OneHotEncoder(
            sparse_output=False, handle_unknown="ignore"
        )

    def _clean_data(self) -> None:
        """Clean the training data by handling missing values and converting data types"""
        if self.df is None:
            raise ValueError("Data not loaded")

        # Handle 'N/A' strings in price column
        self.df["price"] = self.df["price"].replace("N/A", np.nan)

        # Convert price to numeric
        self.df["price"] = pd.to_numeric(self.df["price"], errors="coerce")
        
        # Shared model: prop_type, address, room_type
        # Handle room_type column if it exists as a single categorical column
        if "room_type" in self.df.columns:
            # Convert room_type to string for consistency
            self.df["room_type"] = self.df["room_type"].astype(str)
        
        # Extract Dublin postal codes from address
        self.df["dublin_area"] = self._extract_dublin_postal_code(self.df["address"])
        
        # Drop rows with missing essential data for shared model
        essential_columns = ["price", "prop_type", "dublin_area"]
        if "room_type" in self.df.columns:
            essential_columns.append("room_type")
        
        self.df = self.df.dropna(subset=essential_columns)

        # Filter out unrealistic prices (less than 200 or greater than 20000)
        self.df = self.df[(self.df["price"] >= 200) & (self.df["price"] <= 20000)]

    def prepare_features(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features (X) and target (y) for model training"""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        # Fit and transform categorical features
        prop_type_encoded = self.prop_type_encoder.fit_transform(self.df[["prop_type"]])
        dublin_area_encoded = self.dublin_area_encoder.fit_transform(
            self.df[["dublin_area"]]
        )

        # Create feature names for common categorical features
        prop_type_features = [
            f"prop_type_{cat}" for cat in self.prop_type_encoder.categories_[0]
        ]
        dublin_area_features = [
            f"dublin_area_{int(cat)}" for cat in self.dublin_area_encoder.categories_[0]
        ]

        # Shared model: prop_type (one-hot), address (one-hot), room_type (one-hot)
        if "room_type" in self.df.columns:
            # Fit and transform room_type
            room_type_encoded = self.room_type_encoder.fit_transform(self.df[["room_type"]])
            room_type_features = [
                f"room_type_{cat}" for cat in self.room_type_encoder.categories_[0]
            ]
            
            # Combine all features (no numeric features for shared model)
            X = np.hstack([prop_type_encoded, dublin_area_encoded, room_type_encoded])
            
            # Store feature names
            self.feature_names = (
                prop_type_features + dublin_area_features + room_type_features
            )
        else:
            raise ValueError("room_type column is required for shared model")

        # Target
        y = self.df["price"].values

        self.logger.info(f"Prepared features: {X.shape}")
        self.logger.info(f"Feature names: {self.feature_names}")

        return X, y

    def encode_input(self, input_data: dict) -> np.ndarray:
        """Encode user input for prediction"""
        try:
            # Extract numeric Dublin area from frontend format (e.g., "dublin-1" -> 1)
            dublin_area_numeric = self._extract_numeric_area_from_frontend(input_data.get("address", ""))

            # Prepare data for encoding categorical features
            prop_type_df = pd.DataFrame({"prop_type": [input_data.get("property_type", "")]})
            dublin_area_df = pd.DataFrame({"dublin_area": [dublin_area_numeric]})

            # Transform using fitted encoders
            prop_type_encoded = self.prop_type_encoder.transform(prop_type_df)
            dublin_area_encoded = self.dublin_area_encoder.transform(dublin_area_df)

            # Shared model: prop_type (one-hot), address (one-hot), room_type (one-hot)
            room_type = input_data.get("room_type", "")
            
            if not room_type:
                raise ValueError("room_type is required for shared model predictions")
            
            # Prepare room_type for encoding
            room_type_df = pd.DataFrame({"room_type": [room_type]})
            room_type_encoded = self.room_type_encoder.transform(room_type_df)
            
            # Combine features in the same order as prepare_features (no numeric features)
            X = np.hstack([prop_type_encoded, dublin_area_encoded, room_type_encoded])

            return X

        except Exception as e:
            self.logger.error(f"Error encoding input: {str(e)}")
            raise

    def _save_additional_encoders(self, path_prefix: str) -> None:
        """Save room_type encoder"""
        if self.room_type_encoder is not None:
            joblib.dump(self.room_type_encoder, f"{path_prefix}room_type_encoder.joblib")

    def _load_additional_encoders(self, path_prefix: str) -> None:
        """Load room_type encoder"""
        room_type_encoder_path = f"{path_prefix}room_type_encoder.joblib"
        if os.path.exists(room_type_encoder_path):
            self.room_type_encoder = joblib.load(room_type_encoder_path)
