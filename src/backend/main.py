from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Any
from models.data_processors import PropertyDataProcessor, SharedRoomDataProcessor
from models.predictors import PropertyPricePredictor, SharedRoomPricePredictor

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

    # Load property data and train/load model
    if data_processor.load_data("data/train_property.csv"):
        X_prop, y_prop = data_processor.prepare_features()
        feature_names_prop = data_processor.get_feature_names()

        # Train or load property model
        if model.model_exists():
            try:
                model.load_model()
                data_processor.load_encoders("models/saved_data/property_")
                logger.info("Loaded existing property model")
            except Exception as e:
                logger.warning(f"Failed to load existing property model: {e}")
                logger.info("Training new property model...")
                model.train(X_prop, y_prop, feature_names_prop)
                model.save_model()
                data_processor.save_encoders("models/saved_data/property_")
                logger.info("Property model trained and saved successfully")
        else:
            logger.info("Training new property model...")
            model.train(X_prop, y_prop, feature_names_prop)
            model.save_model()
            data_processor.save_encoders("models/saved_data/property_")
            logger.info("Property model trained and saved successfully")

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

    # Load shared data and train/load model
    if data_processor.load_data("data/train_shared.csv"):
        X_shared, y_shared = data_processor.prepare_features()
        feature_names_shared = data_processor.get_feature_names()

        # Train or load shared model
        if model.model_exists():
            try:
                model.load_model()
                data_processor.load_encoders("models/saved_data/shared_")
                logger.info("Loaded existing shared room model")
            except Exception as e:
                logger.warning(f"Failed to load existing shared room model: {e}")
                logger.info("Training new shared room model...")
                model.train(X_shared, y_shared, feature_names_shared)
                model.save_model()
                data_processor.save_encoders("models/saved_data/shared_")
                logger.info("Shared room model trained and saved successfully")
        else:
            logger.info("Training new shared room model...")
            model.train(X_shared, y_shared, feature_names_shared)
            model.save_model()
            data_processor.save_encoders("models/saved_data/shared_")
            logger.info("Shared room model trained and saved successfully")

    return data_processor, model


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize both ML models on startup"""
    global property_data_processor, property_model, shared_data_processor, shared_model

    try:
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


class PropertyDetails(BaseModel):
    bedrooms: str | None = None
    bathrooms: str | None = None
    propertyType: str
    dublinArea: str
    isShared: bool | None = False
    roomType: str | None = None


@app.post("/predict")
async def predict_rent(details: PropertyDetails) -> dict[str, int]:
    """Predict rental price based on property features"""
    try:
        # Determine which model to use based on isShared flag
        if details.isShared:
            # Validate required fields for shared model
            if not all([details.propertyType, details.dublinArea, details.roomType]):
                raise HTTPException(
                    status_code=400,
                    detail="For shared properties, propertyType, dublinArea, and roomType are required",
                )

            # Get shared model and processor
            model = app.state.shared_model
            processor = app.state.shared_data_processor

            # Prepare input data for shared model
            input_data = {
                "property_type": details.propertyType,
                "address": details.dublinArea,
                "room_type": details.roomType,
            }
        else:
            # Validate required fields for property model
            if not all(
                [
                    details.bedrooms,
                    details.bathrooms,
                    details.propertyType,
                    details.dublinArea,
                ]
            ):
                raise HTTPException(
                    status_code=400,
                    detail="For whole properties, bedrooms, bathrooms, propertyType, and dublinArea are required",
                )

            # Get property model and processor
            model = app.state.property_model
            processor = app.state.property_data_processor

            # Prepare input data for property model
            input_data = {
                "bedrooms": details.bedrooms,
                "bathrooms": details.bathrooms,
                "property_type": details.propertyType,
                "address": details.dublinArea,
            }

        if not model or not model.is_trained:
            raise HTTPException(status_code=500, detail="Model not trained")

        # Encode input features
        try:
            features = processor.encode_input(input_data)
        except Exception as e:
            logger.error(f"Error encoding features: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Unable to process the provided property details",
            )

        # Make prediction
        try:
            predicted_price = model.predict(features)
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Unable to generate price prediction"
            )

        # Return prediction
        return {"predictedPrice": int(round(predicted_price))}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in predict_rent: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request",
        )


@app.get("/model-info")
async def get_model_info(model_type: str | None = "property") -> dict[str, Any]: # Changed parameter
    """Get information about the trained models, based on model_type"""
    try:
        # Determine which model to use based on model_type
        if model_type == "sharing":
            model = app.state.shared_model
            processor = app.state.shared_data_processor
            model_name = "Shared Room Model"
            actual_model_type_name = "shared"
        elif model_type == "property":
            model = app.state.property_model
            processor = app.state.property_data_processor
            model_name = "Property Model"
            actual_model_type_name = "property"
        else: # Default to property model if model_type is invalid or None
            logger.warning(f"Invalid model_type '{model_type}' received, defaulting to property model.")
            model = app.state.property_model
            processor = app.state.property_data_processor
            model_name = "Property Model (default)"
            actual_model_type_name = "property"


        if not model or not processor or not model.is_trained:
            return {
                "feature_importances": {},
                "model_type": f"{actual_model_type_name}_not_trained",
                "status": f"{model_name} not trained or components not initialized",
                "model_metrics": {},
                "data_summary": {},
                "available_options": {"property_types": [], "dublin_areas": []},
            }

        # Get model metrics
        metrics = model.get_metrics()

        # Get feature importance
        feature_importance = model.get_feature_importance()

        # Get data summary
        # The get_data_summary method in the processor might need to be aware of the model type
        # or the data it's processing if it handles both shared/non-shared internally.
        # For now, assuming processor.get_data_summary() correctly returns summary for its type.
        data_summary = processor.get_data_summary()

        # Get available options
        property_types = processor.get_property_types()
        dublin_areas = processor.get_dublin_areas()

        return {
            "feature_importances": feature_importance,
            "model_type": actual_model_type_name, # Reflects the actual model type being reported
            "model_name": model_name,
            "status": f"{model_name} active",
            "model_metrics": metrics,
            "data_summary": data_summary,
            "available_options": {
                "property_types": property_types,
                "dublin_areas": dublin_areas,
            },
        }

    except Exception as e:
        logger.error(f"Error getting model info for {model_type=}: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Unable to retrieve model information"
        )


@app.get("/healthcheck")
async def health_check() -> dict[str, Any]:
    """Health check endpoint"""
    try:
        property_model = app.state.property_model
        shared_model = app.state.shared_model

        property_ready = property_model.is_trained if property_model else False
        shared_ready = shared_model.is_trained if shared_model else False

        overall_ready = property_ready and shared_ready

        return {
            "status": "healthy" if overall_ready else "not_ready",
            "property_model_trained": property_ready,
            "shared_model_trained": shared_ready,
            "both_models_ready": overall_ready,
        }

    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
