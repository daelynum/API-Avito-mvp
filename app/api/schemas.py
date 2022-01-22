from typing import Optional, List
from pydantic import BaseModel, EmailStr


class Towns_schema(BaseModel):
    town_name: str

    class Config:
        orm_mode = True


class Towns_response(Towns_schema):
    id: int


class User_schema(BaseModel):
    email: EmailStr  # Для использования типа EmailStr необходимо установить модуль email-validator:
    mobile_phone: int
    first_name: str
    last_name: str
    town_id: int
    password_hash: str

    class Config:
        orm_mode = True


class Categories_schema(BaseModel):
    category_name: str

    class Config:
        orm_mode = True


class Announcement_schema(BaseModel):
    price: float
    category_id: int
    text: str
    town_id: int

    class Config:
        orm_mode = True


class Favorites_schema(BaseModel):
    id: int
    user_id: int
    announcement_id: int

    class Config:
        orm_mode = True


class ShortModelOfUser(BaseModel):
    first_name: str
    last_name: str
    mobile_phone: int
    email: str
    town: Towns_schema

    class Config:
        orm_mode = True


class ShowFav(Favorites_schema):
    announcement: Announcement_schema
    user: ShortModelOfUser

    class Config:
        orm_mode = True


class ShowUser(BaseModel):
    first_name: str
    last_name: str
    mobile_phone: int
    id: int
    email: str
    town: Towns_schema
    announcement: List[Announcement_schema]
    favorite: List[ShowFav]

    class Config:
        orm_mode = True


class User_announcement_mode(BaseModel):
    first_name: str
    last_name: str
    mobile_phone: int
    id: int
    email: str
    town: Towns_schema

    class Config:
        orm_mode = True


class Images_schema(BaseModel):
    data_path: str
    announcement_id: int

    class Config:
        orm_mode = True


class Show_Images(BaseModel):
    data_path: str

    class Config:
        orm_mode = True


class Announcement_schema_response(BaseModel):
    user: User_announcement_mode
    price: float
    category: Categories_schema
    text: str
    town: Towns_schema
    image: List[Show_Images]

    class Config:
        orm_mode = True


class Show_Categories(BaseModel):
    category_name: str
    id: int

    class Config:
        orm_mode = True


class TokenData(BaseModel):
    name: Optional[str] = None
