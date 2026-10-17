import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, Token, UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["认证"])  # 这个文件里的接口都挂在 /auth 下面


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    """注册：邮箱已存在返回 409，成功返回 201 和用户信息。"""
    # 先主动查一次，为了给出友好的 409，而不是等数据库唯一索引报错
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该邮箱已被注册",
        )

    user = User(
        email=payload.email,
        nickname=payload.nickname,
        password_hash=hash_password(payload.password),  # 只存哈希，明文绝不落库
        invite_code=secrets.token_urlsafe(9),  # 生成 12 位邀请码，给后面配对另一半用
    )
    db.add(user)

    try:
        await db.commit()
    except IntegrityError:
        # 兜底：万一两个请求同时注册同一个邮箱，唯一索引会在这里报错
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该邮箱已被注册",
        )

    return user


@router.post("/login", response_model=Token)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> Token:
    """登录：邮箱不存在和密码错误都返回同一个 401，不告诉对方是哪个错了。"""
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
        )

    return Token(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=UserOut)
async def read_me(current_user: User = Depends(get_current_user)) -> User:
    """当前登录用户：这个接口必须带 token 才进得来。"""
    return current_user