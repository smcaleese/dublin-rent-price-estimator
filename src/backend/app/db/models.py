from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import Base
from passlib.context import CryptContext

# Import UserCreateSchema from the schemas module at the app level
from app import schemas


# This context is for password hashing.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    @classmethod
    async def get_by_email(cls, db: AsyncSession, email: str):
        statement = select(cls).where(cls.email == email)
        result = await db.execute(statement)
        return result.scalars().first()

    @classmethod
    async def create(
        cls, db: AsyncSession, user_data: schemas.UserCreateSchema
    ):  # Use schemas.UserCreateSchema
        hashed_password = pwd_context.hash(user_data.password)
        db_user = cls(email=user_data.email, hashed_password=hashed_password)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    def verify_password(self, plain_password: str):
        return pwd_context.verify(plain_password, self.hashed_password)
