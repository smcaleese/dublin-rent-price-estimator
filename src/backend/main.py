from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI()

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


def calculate_prediction(details: PropertyDetails) -> int:
    # Logic from simulatePrediction
    base_price = 1200
    bedroom_multiplier = int(details.bedrooms) * 400
    bathroom_multiplier = int(details.bathrooms) * 200

    area_multiplier = 1.0
    if details.dublinArea in ["dublin-1", "dublin-2", "dublin-4"]:
        area_multiplier = 1.4
    elif details.dublinArea in ["dublin-6", "blackrock", "dun-laoghaire"]:
        area_multiplier = 1.2
    elif details.dublinArea in ["howth", "malahide"]:
        area_multiplier = 1.1

    type_multiplier = 1.0
    if details.propertyType == "house":
        type_multiplier = 1.3
    elif details.propertyType == "townhouse":
        type_multiplier = 1.2
    elif details.propertyType == "duplex":
        type_multiplier = 1.15
    elif details.propertyType == "studio":
        type_multiplier = 0.7

    prediction = round(
        (base_price + bedroom_multiplier + bathroom_multiplier)
        * area_multiplier
        * type_multiplier
    )
    return prediction


@app.post("/predict")
async def predict_rent(details: PropertyDetails):
    prediction = calculate_prediction(details)
    return {"predictedPrice": prediction}


@app.get("/healthcheck")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
