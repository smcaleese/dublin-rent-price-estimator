from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging
from contextlib import asynccontextmanager
from models import DataProcessor, RentalPricePredictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
data_processor = None
ml_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize ML model on startup"""
    global data_processor, ml_model
    
    try:
        logger.info("Initializing ML components...")
        
        # Initialize data processor and model
        data_processor = DataProcessor()
        ml_model = RentalPricePredictor()
        
        # Always load and process data to ensure encoders are fitted
        data_processor.load_data('data/train.csv')
        X, y = data_processor.prepare_features()
        feature_names = data_processor.get_feature_names()
        
        # Train model if not already trained
        if ml_model.model_exists():
            try:
                ml_model.load_model()
                logger.info("Loaded existing trained model")
            except Exception as e:
                logger.warning(f"Failed to load existing model: {e}")
                logger.info("Training new model...")
                ml_model.train(X, y, feature_names)
                ml_model.save_model()
                logger.info("Model trained and saved successfully")
        else:
            logger.info("Training new model...")
            ml_model.train(X, y, feature_names)
            ml_model.save_model()
            logger.info("Model trained and saved successfully")
        
        # Store in app context for easy access
        app.state.data_processor = data_processor
        app.state.ml_model = ml_model
        
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
    bedrooms: str
    bathrooms: str
    propertyType: str
    dublinArea: str


@app.post("/predict")
async def predict_rent(details: PropertyDetails):
    """Predict rental price based on property features"""
    try:
        # Validate required fields
        if not all([details.bedrooms, details.bathrooms, details.propertyType, details.dublinArea]):
            raise HTTPException(
                status_code=400,
                detail="All fields are required: bedrooms, bathrooms, propertyType, dublinArea"
            )
        
        # Get model and data processor
        model = app.state.ml_model
        processor = app.state.data_processor
        
        if not model.is_trained:
            raise HTTPException(
                status_code=500,
                detail="Model not trained"
            )
        
        # Encode input features
        try:
            features = processor.encode_input(
                details.bedrooms,
                details.bathrooms,
                details.propertyType,
                details.dublinArea
            )
        except Exception as e:
            logger.error(f"Error encoding features: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Unable to process the provided property details"
            )
        
        # Make prediction
        try:
            predicted_price = model.predict(features)
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Unable to generate price prediction"
            )
        
        # Return prediction
        return {
            "predictedPrice": int(round(predicted_price))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in predict_rent: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request"
        )


@app.get("/model-info")
async def get_model_info():
    """Get information about the trained model"""
    try:
        model = app.state.ml_model
        processor = app.state.data_processor
        
        if not model.is_trained:
            return {
                "feature_importances": {},
                "model_type": "not_trained",
                "status": "Model not trained"
            }
        
        # Get model metrics
        metrics = model.get_metrics()
        
        # Get feature importance
        feature_importance = model.get_feature_importance()
        
        # Get data summary
        data_summary = processor.get_data_summary()
        
        # Get available options
        property_types = processor.get_property_types()
        dublin_areas = processor.get_dublin_areas()
        
        return {
            "feature_importances": feature_importance,
            "model_type": "RandomForestRegressor",
            "status": "ML model active",
            "model_metrics": metrics,
            "data_summary": data_summary,
            "available_options": {
                "property_types": property_types,
                "dublin_areas": dublin_areas
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve model information"
        )


@app.get("/healthcheck")
async def health_check():
    """Health check endpoint"""
    try:
        model = app.state.ml_model
        is_ready = model.is_trained if model else False
        
        return {
            "status": "healthy" if is_ready else "not_ready",
            "model_trained": is_ready
        }
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
