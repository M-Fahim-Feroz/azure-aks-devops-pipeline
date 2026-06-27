from typing import Optional
from sqlmodel import Field, SQLModel


# User Models
class UserBase(SQLModel):
    first_name: str
    last_name: str
    mail: str
    age: int


class User(UserBase, table=True):
    __tablename__ = "User"
    id: Optional[int] = Field(default=None, primary_key=True)


class UserIn(UserBase):
    pass


class UserOut(UserBase):
    id: int


# Weather Models
class WeatherBase(SQLModel):
    city: str = Field(index=True)
    date: str
    day: str
    description: str
    degree: float


class Weather(WeatherBase, table=True):
    __tablename__ = "Weather"
    id: Optional[int] = Field(default=None, primary_key=True)


class WeatherIn(WeatherBase):
    pass


class WeatherOut(SQLModel):
    date: str
    day: str
    description: str
    degree: float
