from typing import List
from pydantic import BaseModel, Field, EmailStr


class Photo(BaseModel):
    url: str
    name: str
    vote: int
    thumbnail_url: str
    square_url: str
    userid: str


class Albums(BaseModel):
    name: str
    photos: List[Photo]
    userid: str


class Summary(BaseModel):
    top_weekly: List[str] = []
    top_monthly: List[str] = []
    top_daily: List[str] = []


class UserSchema(BaseModel):
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "fullname": "Abdulazeez Abdulazeez Adeshina",
                "email": "abdulazeez@x.com",
                "password": "weakpassword"
            }
        }


class UserSchema(BaseModel):
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "fullname": "Abdulazeez Abdulazeez Adeshina",
                "email": "abdulazeez@x.com",
                "password": "weakpassword"
            }
        }


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "email": "abdulazeez@x.com",
                "password": "weakpassword"
            }
        }
