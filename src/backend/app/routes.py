from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import logging
from typing import Any
from sqlalchemy.orm import Session

from .db.session import get_db
from .db.models import User
from .auth import create_access_token, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
from . import schemas # Import the new schemas module
from datetime import timedelta

# Configure logging
logger = logging.getLogger(__name__)

# Create the router
router = APIRouter()

# --- Authentication Endpoints ---

@router.post("/signup", response_model=schemas.UserResponseSchema)
async def signup(user_data: schemas.UserCreateSchema, db: Session = Depends(get_db)):
    db_user = User.get_by_email(db, email=user_data.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Use the aliased DbUserCreateSchema for creating user in DB if it's different
    # For now, UserCreateSchema is compatible with User.create method's expectation
    created_user = User.create(db=db, user_data=user_data)
    return created_user

@router.post("/login", response_model=schemas.TokenSchema)
async def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = User.get_by_email(db, email=form_data.username) # form_data.username is the email
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.UserResponseSchema)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# --- Existing Endpoints ---

class PropertyDetails(BaseModel):
    bedrooms: str | None = None
    bathrooms: str | None = None
    propertyType: str
    dublinArea: str
    isShared: bool | None = False
    roomType: str | None = None


@router.post("/predict")
async def predict_rent(details: PropertyDetails, request: Request) -> dict[str, Any]:
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
            model = request.app.state.shared_model
            processor = request.app.state.shared_data_processor

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
            model = request.app.state.property_model
            processor = request.app.state.property_data_processor

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
            prediction_result = model.predict(features)
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Unable to generate price prediction"
            )

        # Return prediction with confidence interval
        return {
            "predictedPrice": int(round(prediction_result["prediction"])),
            "lowerBound": int(round(prediction_result["lower_bound"])),
            "upperBound": int(round(prediction_result["upper_bound"])),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in predict_rent: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request",
        )


@router.get("/model-info")
async def get_model_info(request: Request, model_type: str | None = "property") -> dict[str, Any]:
    """Get information about the trained models, based on model_type"""
    try:
        # Determine which model to use based on model_type
        if model_type == "sharing":
            model = request.app.state.shared_model
            processor = request.app.state.shared_data_processor
            model_name = "Shared Room Model"
            actual_model_type_name = "shared"
        elif model_type == "property":
            model = request.app.state.property_model
            processor = request.app.state.property_data_processor
            model_name = "Property Model"
            actual_model_type_name = "property"
        else: # Default to property model if model_type is invalid or None
            logger.warning(f"Invalid model_type '{model_type}' received, defaulting to property model.")
            model = request.app.state.property_model
            processor = request.app.state.property_data_processor
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


@router.get("/healthcheck")
async def health_check(request: Request) -> dict[str, Any]:
    """Health check endpoint"""
    try:
        property_model = request.app.state.property_model
        shared_model = request.app.state.shared_model

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
