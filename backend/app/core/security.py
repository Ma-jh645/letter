"""密码哈希 + JWT 令牌的签发与校验。"""

from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def hash_password(plain: str) -> str:
    """把明文密码转成不可逆的哈希串。"""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """校验明文密码是否与哈希串匹配。"""
    return pwd_context.verify(plain, hashed)


def create_access_token(subject: str) -> str:
    """签发一个 access token，subject 传 user.id。"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": str(subject), "exp": expire}  #把userid也就是subject字符串化
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM) #这里是把字符串化的userid编进jwt中


def  decode_access_token(token: str) -> str | None:
    """解出 token 里的 user.id；任何异常都返回 None。"""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM]) #这里的返回值是字符串，因为jwt是json形式，里面只能装str形式的uesrid，不能装uuid形式的userid
    except jwt.InvalidTokenError:
        return None
    return payload.get("sub")