from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Any
from app.models.data_processors import PropertyDataProcessor, SharedRoomDataProcessor
from app.models.predictors import PropertyPricePredictor, SharedRoomPricePredictor
from app.routes import router
from app.db.session import init_db as initialize_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances for property model
property_data_processor: PropertyDataProcessor | None = None
property_model: PropertyPricePredictor | None = None

# Global instances for shared room model
shared_data_processor: SharedRoomDataProcessor | None = None
shared_model: SharedRoomPricePredictor | None = None


def initialize_property_model() -> tuple[PropertyDataProcessor, PropertyPricePredictor]:
    """Initialize and train/load the property model"""
    logger.info("Setting up property model...")

    # Initialize property model components
    data_processor = PropertyDataProcessor()
    model = PropertyPricePredictor(
        model_path="models/saved_data/property_model.joblib",
        metrics_path="models/saved_data/property_model_metrics.json",
    )

    # Try to load existing model first
    if model.model_exists():
        try:
            model.load_model()
            data_processor.load_encoders("models/saved_data/property_")
            logger.info("Loaded existing property model successfully")
            return data_processor, model
        except Exception as e:
            logger.warning(f"Failed to load existing property model: {e}")
            logger.info("Will train new model instead...")

    # If no model exists or loading failed, load data and train
    logger.info("Loading training data for property model...")
    if data_processor.load_data("app/data/train_property.csv"):
        X_prop, y_prop = data_processor.prepare_features()
        feature_names_prop = data_processor.get_feature_names()

        logger.info("Training new property model...")
        model.train(X_prop, y_prop, feature_names_prop)
        model.save_model()
        data_processor.save_encoders("models/saved_data/property_")
        logger.info("Property model trained and saved successfully")
    else:
        logger.error("Failed to load property training data")
        raise RuntimeError("Cannot initialize property model without training data")

    return data_processor, model


def initialize_shared_model() -> tuple[
    SharedRoomDataProcessor, SharedRoomPricePredictor
]:
    """Initialize and train/load the shared room model"""
    logger.info("Setting up shared room model...")

    # Initialize shared room model components
    data_processor = SharedRoomDataProcessor()
    model = SharedRoomPricePredictor(
        model_path="models/saved_data/shared_model.joblib",
        metrics_path="models/saved_data/shared_model_metrics.json",
    )

    # Try to load existing model first
    if model.model_exists():
        try:
            model.load_model()
            data_processor.load_encoders("models/saved_data/shared_")
            logger.info("Loaded existing shared room model successfully")
            return data_processor, model
        except Exception as e:
            logger.warning(f"Failed to load existing shared room model: {e}")
            logger.info("Will train new model instead...")

    # If no model exists or loading failed, load data and train
    logger.info("Loading training data for shared room model...")
    if data_processor.load_data("app/data/train_shared.csv"):
        X_shared, y_shared = data_processor.prepare_features()
        feature_names_shared = data_processor.get_feature_names()

        logger.info("Training new shared room model...")
        model.train(X_shared, y_shared, feature_names_shared)
        model.save_model()
        data_processor.save_encoders("models/saved_data/shared_")
        logger.info("Shared room model trained and saved successfully")
    else:
        logger.error("Failed to load shared room training data")
        raise RuntimeError("Cannot initialize shared room model without training data")

    return data_processor, model


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize both ML models on startup"""
    global property_data_processor, property_model, shared_data_processor, shared_model

    try:
        logger.info("Initializing database...")
        await initialize_database()  # Call the database initializer
        logger.info("Database initialization complete.")

        logger.info("Initializing ML components...")

        # Initialize property model using the dedicated function
        property_data_processor, property_model = initialize_property_model()

        # Initialize shared room model using the dedicated function
        shared_data_processor, shared_model = initialize_shared_model()

        # Store all components in app context for easy access
        app.state.property_data_processor = property_data_processor
        app.state.property_model = property_model
        app.state.shared_data_processor = shared_data_processor
        app.state.shared_model = shared_model

        yield

    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise
    finally:
        logger.info("Shutting down...")


app = FastAPI(lifespan=lifespan)

# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL e.g. "http://localhost:3000"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


if __name__ == "__main__":
    # To run this app for development, stand in the `src/backend` directory
    # and run the following command in your terminal:
    # uvicorn app.main:app --reload
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
