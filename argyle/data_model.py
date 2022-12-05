from pydantic import BaseModel, validator
import uuid
import re
from typing import Optional


class CountryFormatError(Exception):
    """
    Custom error raised when the country field has the wrong format
    """
    def __init__(self, value: str, message: str) -> None:
        self.value = value
        self.message = message
        super().__init__(message)


class InvalidPhoneNumber(Exception):
    """
    Custom error raised when the phone number is not in E.164 format
    """
    def __init__(self, value: str, message: str) -> None:
        self.value = value
        self.message = message
        super().__init__(message)


class Address(BaseModel):
    line1: str
    line2: str
    city: str
    state: str
    postal_code: str
    country: str

    @validator("country")
    def valid_country_name_format(cls, value: str) -> bool:
        """
        Validator that checks if country value is in ISO 3166-1 alpha-2 format
        """
        if len(value) > 2:
            raise CountryFormatError(value=value, message="Invalid value format for field Country")
        return True


class UpworkUser(BaseModel):
    id: str
    account: str
    employer: str
    first_name: str
    last_name: str
    full_name: str
    email: str
    phone_number: str
    birth_date: str
    picture_url: str
    address: Address
    ssn: str
    martial_status: str
    gender: str
    metadata: Optional[dict]
    created_at: str
    updated_at: str

    @validator('id', 'account')
    def is_valid_uuid(cls, value: str) -> bool:
        """
        Validator that checks if the value is a valid UUID.
        """
        try:
            uuid.UUID(str(value))
            return True
        except ValueError:
            return False

    @validator('phone_number')
    def is_phone_number_valid(cls, value: str) -> bool:
        if not re.search(r"^\+[1-9]\d{1,14}$", value):
            raise InvalidPhoneNumber(value=value, message="Phone number is not in E.164 format")
        return True
