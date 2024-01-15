from pydantic import BaseModel
from src.models import intpk, created_at_type


class UserBase(BaseModel):

    id: intpk | None = None
    nickname: str | None = None
    date_registration: created_at_type | None = None


class UserCreateDTO(BaseModel):

    email: str
    password: str
    nickname: str

class UserDTO(BaseModel):
    nickname: str
    id: intpk
    email: str
    avatar_path: str | None = None
    is_admin: bool | None = None
    is_locked: bool | None = None

    class Config:
        from_attributes = True


class UserRefreshDTO(UserBase):

    avatar_path: str | None = None
    is_admin: bool | None = None
    is_locked: bool | None = None
    access_token: str | None = None
    email: str | None = None

    class Config:
        from_attributes = True

class UserLoginDTO(UserBase):

    access_token: str
    refresh_token: str

class UserChangePasswordDTO(BaseModel):

    old_password: str
    new_password: str

class UserChangeNameDTO(BaseModel):

    new_name: str

class GetSecureCodeDTO(BaseModel):

    secure_code: int

class UserAuthenticationDTO(BaseModel):

    email: str
    password: str


