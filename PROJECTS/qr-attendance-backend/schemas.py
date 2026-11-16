from pydantic import BaseModel, EmailStr
from datetime import date


class MemberCreate(BaseModel):
    first_name: str
    last_name: str
    gender: str
    dob: date

    email: EmailStr
    phone: str

    home_address: str
    city: str
    state: str
    zip_code: str

    occupation: str
    membership_type_preference: str

    marital_status: str
    family_details: str | None = None

    passport_photo_submitted: str

    spiritual_information: str | None = None

    baptized: str
    previously_part_of_church: str


class ScanRequest(BaseModel):
    qr_id: str  # Matches Member.qr_id column
    session_id: str


class ScanResponse(BaseModel):
    status: str
    message: str
    name: str