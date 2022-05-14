from typing import List
from pydantic import BaseModel


class Photo(BaseModel):
    url: str
    name: str
    vote: int
    thumbnail_url: str
    square_url: str
    userid: str


class User(BaseModel):
    username: str
    password: str


class Summary(BaseModel):
    top_weekly: List[str] = []
    top_monthly: List[str] = []
    top_daily: List[str] = []
