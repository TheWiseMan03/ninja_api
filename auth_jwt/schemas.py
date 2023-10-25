from ninja import Schema
from typing import Optional


class TokenPayload(Schema):
    user_id: int = None


class RegistrationSchema(Schema):
    username: str
    password: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]


class PasswordUpdateSchema(Schema):
    username: str
    password: str
    new_password: str


class UpdateSchema(Schema):
    username: Optional[str]
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]


class UserLoginSchema(Schema):
    username: str
    password: str


class RefreshTokenSchema(Schema):
    refresh_token: str
