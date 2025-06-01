import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import OneHotEncoder
import logging
import os
import joblib
import json
from typing import Optional, Any, Tuple


class DataProcessor:
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

    def _clean_data(self) -> None:
        """Clean the training data by handling missing values and converting data types"""
        if self.df is None:
            raise ValueError("Data not loaded")

        # Handle 'N/A' strings in price column
        self.df["price"] = self.df["price"].replace("N/A", np.nan)

        # Convert columns to numeric, coercing errors to NaN
        self.df["price"] = pd.to_numeric(self.df["price"], errors="coerce")
        self.df["beds"] = pd.to_numeric(self.df["beds"], errors="coerce")
        self.df["baths"] = pd.to_numeric(self.df["baths"], errors="coerce")
        
        # Handle new sharing-related columns if they exist
        if "is_shared" in self.df.columns:
            self.df["is_shared"] = pd.to_numeric(self.df["is_shared"], errors="coerce").fillna(0)
        else:
            self.df["is_shared"] = 0
            
        # Handle room_type columns if they exist
        room_type_cols = ["room_type_single", "room_type_double", "room_type_twin", "room_type_shared"]
        for col in room_type_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors="coerce").fillna(0)
            else:
                self.df[col] = 0

        # Extract Dublin postal codes
        self.df["dublin_area"] = self._extract_dublin_postal_code(self.df["address"])

        # Drop rows with missing essential data
        self.df = self.df.dropna(
            subset=["price", "beds", "baths", "prop_type", "dublin_area"]
        )

        # Filter out unrealistic prices (less than 200 or greater than 20000)
        # Lowered minimum for shared rooms which can be cheaper
        self.df = self.df[(self.df["price"] >= 200) & (self.df["price"] <= 20000)]

    def _extract_dublin_postal_code(self, address_series: pd.Series) -> pd.Series:
        """Extract numeric Dublin postal codes from address strings"""

        def extract_code(address: Any) -> Any:
            if pd.isna(address):
                return np.nan

            # Convert to string and make uppercase for consistent matching
            address_str = str(address).upper()

            # Pattern 1: "Dublin X" where X is 1-2 digits
            match = re.search(r"DUBLIN\s+(\d{1,2})", address_str)
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

    def prepare_features(self) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features (X) and target (y) for model training"""
        if self.df is None:
            raise ValueError("Data not loaded. Call load_data() first.")

        # Fit and transform categorical features
        prop_type_encoded = self.prop_type_encoder.fit_transform(self.df[["prop_type"]])
        dublin_area_encoded = self.dublin_area_encoder.fit_transform(
            self.df[["dublin_area"]]
        )

        # Create feature names
        prop_type_features = [
            f"prop_type_{cat}" for cat in self.prop_type_encoder.categories_[0]
        ]
        dublin_area_features = [
            f"dublin_area_{int(cat)}" for cat in self.dublin_area_encoder.categories_[0]
        ]

        # Prepare numeric features including sharing-related features
        numeric_features = ["beds", "baths", "is_shared", "room_type_single", "room_type_double", "room_type_twin", "room_type_shared"]
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

    def encode_input(self, bedrooms: str, bathrooms: str, property_type: str, dublin_area: str, 
                    is_shared: bool = False, room_type: str = None) -> np.ndarray:
        """Encode user input for prediction"""
        try:
            # Convert bedrooms and bathrooms to numeric
            beds = pd.to_numeric(bedrooms, errors="coerce")
            baths = pd.to_numeric(bathrooms, errors="coerce")

            # Handle NaN values with defaults
            if pd.isna(beds):
                beds = 1
            if pd.isna(baths):
                baths = 1

            # Handle sharing-related features
            is_shared_val = 1 if is_shared else 0
            
            # Initialize room type features
            room_type_single = 0
            room_type_double = 0
            room_type_twin = 0
            room_type_shared = 0
            
            # Set room type if shared
            if is_shared and room_type:
                if room_type.lower() == "single":
                    room_type_single = 1
                elif room_type.lower() == "double":
                    room_type_double = 1
                elif room_type.lower() == "twin":
                    room_type_twin = 1
                elif room_type.lower() == "shared":
                    room_type_shared = 1

            # Extract numeric Dublin area from frontend format (e.g., "dublin-1" -> 1)
            dublin_area_numeric = self._extract_numeric_area_from_frontend(dublin_area)

            # Prepare data for encoding
            prop_type_df = pd.DataFrame({"prop_type": [property_type]})
            dublin_area_df = pd.DataFrame({"dublin_area": [dublin_area_numeric]})

            # Transform using fitted encoders
            prop_type_encoded = self.prop_type_encoder.transform(prop_type_df)
            dublin_area_encoded = self.dublin_area_encoder.transform(dublin_area_df)

            # Combine features in the same order as prepare_features
            X_numeric = np.array([[beds, baths, is_shared_val, room_type_single, 
                                 room_type_double, room_type_twin, room_type_shared]])
            X = np.hstack([X_numeric, prop_type_encoded, dublin_area_encoded])

            return X

        except Exception as e:
            self.logger.error(f"Error encoding input: {str(e)}")
            raise

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

    def get_data_summary(self, shared_filter: bool | None = None) -> dict[str, Any]:
        """Get summary statistics of the data, optionally filtered by shared status"""
        if self.df is None:
            return {}

        df_to_summarize = self.df
        if shared_filter is True:
            df_to_summarize = self.df[self.df["is_shared"] == 1]
        elif shared_filter is False:
            df_to_summarize = self.df[self.df["is_shared"] == 0]
        
        if df_to_summarize.empty:
            return {
                "total_records": 0,
                "avg_price": 0,
                "min_price": 0,
                "max_price": 0,
                "property_types": {},
                "dublin_areas": {},
                "message": "No data for selected filter."
            }

        return {
            "total_records": len(df_to_summarize),
            "avg_price": float(df_to_summarize["price"].mean()) if not df_to_summarize["price"].empty else 0,
            "min_price": float(df_to_summarize["price"].min()) if not df_to_summarize["price"].empty else 0,
            "max_price": float(df_to_summarize["price"].max()) if not df_to_summarize["price"].empty else 0,
            "property_types": df_to_summarize["prop_type"].value_counts().to_dict(),
            "dublin_areas": df_to_summarize["dublin_area"].value_counts().to_dict(),
        }

    def get_feature_names(self) -> list[str]:
        """Get the feature names after encoding"""
        return self.feature_names.copy() if self.feature_names else []
