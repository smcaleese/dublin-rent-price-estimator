from pydantic import BaseModel
from datetime import datetime # Added
from typing import Any, Dict # Added

# --- Pydantic Schemas for User Authentication ---
class UserBase(BaseModel):
    email: str

class UserCreateSchema(UserBase):
    password: str

class UserResponseSchema(UserBase):
    id: int

    class Config:
        from_attributes = True

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

class TokenDataSchema(BaseModel):
    email: str | None = None

# --- Pydantic Schemas for Search History ---
class SearchHistoryBaseSchema(BaseModel):
    search_parameters: Dict[str, Any]
    prediction_result: Dict[str, Any]

class SearchHistoryCreateSchema(SearchHistoryBaseSchema):
    pass

class SearchHistoryResponseSchema(SearchHistoryBaseSchema):
    id: int
    user_id: int # Added user_id for response clarity
    timestamp: datetime

    class Config:
        from_attributes = True
