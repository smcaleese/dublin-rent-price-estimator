from pydantic import BaseModel

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
