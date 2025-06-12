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
    search_parameters: dict[str, Any]
    prediction_result: dict[str, Any]

class SearchHistoryCreateSchema(SearchHistoryBaseSchema):
    pass

class SearchHistoryResponseSchema(SearchHistoryBaseSchema):
    id: int
    user_id: int
    search_parameters: dict[str, Any]
    prediction_result: dict[str, Any]

    class Config:
        from_attributes = True
