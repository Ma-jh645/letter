import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False) #FastAPI 自带的「从请求头里抠 token」的小工具，得到token


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme), #依赖注入，先运行括号里面的方法，得到结果赋值(token)
    db: AsyncSession = Depends(get_db), #依赖注入，先运行括号里面的方法，得到结果赋值（数据库会话）
) -> User:
    """从请求头里的 JWT 解析出当前登录用户，失败一律返回 401。"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供登录凭证",
            headers={"WWW-Authenticate": "Bearer"}, #响应头
        )

    subject = decode_access_token(credentials.credentials) #token(jwt)中提取字符串形式的userid(subject)
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录凭证无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = uuid.UUID(subject) #把字符串形式的subject转成uuid形式的userid
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录凭证无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user