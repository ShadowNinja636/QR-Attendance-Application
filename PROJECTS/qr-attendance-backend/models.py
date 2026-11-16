from sqlalchemy import Column, String, Integer, Date, Time, ForeignKey
from database import Base

class Member(Base):
    __tablename__ = "members"

    member_id = Column(Integer, primary_key=True, index=True)

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    gender = Column(String(20), nullable=False)

    email = Column(String(150), nullable=False)
    phone = Column(String(20), nullable=False)

    home_address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    zip_code = Column(String(20), nullable=False)

    occupation = Column(String(150), nullable=False)
    membership_type_preference = Column(String(150), nullable=False)

    marital_status = Column(String(100), nullable=False)
    family_details = Column(String(500), nullable=True)

    passport_photo_submitted = Column(String(10), nullable=False)

    spiritual_information = Column(String(500), nullable=True)

    baptized = Column(String(10), nullable=False)
    previously_part_of_church = Column(String(10), nullable=False)

    qr_id = Column(String(50), unique=True, nullable=False)
    dob = Column(Date)


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    
    # Updated ForeignKey to match the new 'member_id' column in Members
    member_id = Column(Integer, ForeignKey("members.member_id"))
    
    date = Column(Date)
    time = Column(Time)
    session_id = Column(String(50))