import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.customer import AccountStatus


class CustomerBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone_number: str | None = Field(default=None, max_length=30)
    date_of_birth: date
    address: str | None = Field(default=None, max_length=500)
    account_status: AccountStatus = AccountStatus.ACTIVE
    credit_score: int = Field(ge=300, le=850)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone_number: str | None = Field(default=None, max_length=30)
    date_of_birth: date | None = None
    address: str | None = Field(default=None, max_length=500)
    account_status: AccountStatus | None = None
    credit_score: int | None = Field(default=None, ge=300, le=850)


class CustomerRead(CustomerBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
