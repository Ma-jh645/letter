import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """用户注册格式"""
    email: EmailStr
    nickname: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=6, max_length=72)


class LoginRequest(BaseModel):
    """用户登录格式"""
    email: EmailStr
    password: str


class UserOut(BaseModel):
    """服务器向用户发送用户信息"""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    nickname: str
    invite_code: str
    partner_id: uuid.UUID | None
    created_at: datetime


class Token(BaseModel):
    """服务器向用户发送通行证（token）信息"""
    access_token: str
    token_type: str = "bearer"