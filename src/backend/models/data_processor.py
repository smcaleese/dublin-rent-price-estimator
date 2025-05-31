import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import OneHotEncoder
import logging
import os
import joblib
import json


class DataProcessor:
    def __init__(self):
        self.df = None
        self.prop_type_encoder = OneHotEncoder(
            sparse_output=False, handle_unknown="ignore"
        )
        self.dublin_area_encoder = OneHotEncoder(
            sparse_output=False, handle_unknown="ignore"
        )
        self.feature_names = None
        self.logger = logging.getLogger(__name__)

    def load_data(self, file_path):
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

    def _clean_data(self):
        """Clean the training data by handling missing values and converting data types"""
        if self.df is None:
            raise ValueError("Data not loaded")

        # Handle 'N/A' strings in price column
        self.df["price"] = self.df["price"].replace("N/A", np.nan)

        # Convert columns to numeric, coercing errors to NaN
        self.df["price"] = pd.to_numeric(self.df["price"], errors="coerce")
        self.df["beds"] = pd.to_numeric(self.df["beds"], errors="coerce")
        self.df["baths"] = pd.to_numeric(self.df["baths"], errors="coerce")

        # Extract Dublin postal codes
        self.df["dublin_area"] = self._extract_dublin_postal_code(self.df["address"])

        # Drop rows with missing essential data
        self.df = self.df.dropna(
            subset=["price", "beds", "baths", "prop_type", "dublin_area"]
        )

        # Filter out unrealistic prices (less than 500 or greater than 20000)
        self.df = self.df[(self.df["price"] >= 500) & (self.df["price"] <= 20000)]

    def _extract_dublin_postal_code(self, address_series):
        """Extract numeric Dublin postal codes from address strings"""

        def extract_code(address):
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

    def prepare_features(self):
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

        # Combine all features
        X_numeric = self.df[["beds", "baths"]].values
        X = np.hstack([X_numeric, prop_type_encoded, dublin_area_encoded])

        # Store feature names
        self.feature_names = (
            ["beds", "baths"] + prop_type_features + dublin_area_features
        )

        # Target
        y = self.df["price"].values

        self.logger.info(f"Prepared features: {X.shape}")
        self.logger.info(f"Feature names: {self.feature_names}")

        return X, y

    def encode_input(self, bedrooms, bathrooms, property_type, dublin_area):
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

            # Extract numeric Dublin area from frontend format (e.g., "dublin-1" -> 1)
            dublin_area_numeric = self._extract_numeric_area_from_frontend(dublin_area)

            # Prepare data for encoding
            prop_type_df = pd.DataFrame({"prop_type": [property_type]})
            dublin_area_df = pd.DataFrame({"dublin_area": [dublin_area_numeric]})

            # Transform using fitted encoders
            prop_type_encoded = self.prop_type_encoder.transform(prop_type_df)
            dublin_area_encoded = self.dublin_area_encoder.transform(dublin_area_df)

            # Combine features
            X_numeric = np.array([[beds, baths]])
            X = np.hstack([X_numeric, prop_type_encoded, dublin_area_encoded])

            return X

        except Exception as e:
            self.logger.error(f"Error encoding input: {str(e)}")
            raise

    def _extract_numeric_area_from_frontend(self, dublin_area_str):
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

    def get_property_types(self):
        """Get list of available property types"""
        if (
            hasattr(self.prop_type_encoder, "categories_")
            and len(self.prop_type_encoder.categories_) > 0
        ):
            return self.prop_type_encoder.categories_[0].tolist()
        return ["Apartment", "House", "Studio"]

    def get_dublin_areas(self):
        """Get list of available Dublin areas"""
        if (
            hasattr(self.dublin_area_encoder, "categories_")
            and len(self.dublin_area_encoder.categories_) > 0
        ):
            return sorted(
                [int(area) for area in self.dublin_area_encoder.categories_[0]]
            )
        return []

    def get_data_summary(self):
        """Get summary statistics of the data"""
        if self.df is None:
            return {}

        return {
            "total_records": len(self.df),
            "avg_price": float(self.df["price"].mean()),
            "min_price": float(self.df["price"].min()),
            "max_price": float(self.df["price"].max()),
            "property_types": self.df["prop_type"].value_counts().to_dict(),
            "dublin_areas": self.df["dublin_area"].value_counts().to_dict(),
        }

    def get_feature_names(self):
        """Get the feature names after encoding"""
        return self.feature_names.copy() if self.feature_names else []
