"""
Models package for the Dublin Rent Price Estimator.

This package contains the machine learning models and data processing classes.
"""

# Import new consolidated classes
from .data_processors import BaseDataProcessor, PropertyDataProcessor, SharedRoomDataProcessor
from .predictors import BasePricePredictor, PropertyPricePredictor, SharedRoomPricePredictor

__all__ = [
    # New classes
    'BaseDataProcessor', 'PropertyDataProcessor', 'SharedRoomDataProcessor',
    'BasePricePredictor', 'PropertyPricePredictor', 'SharedRoomPricePredictor',
]
