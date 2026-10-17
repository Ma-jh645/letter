from fastapi import FastAPI

from app.api.routes import health,auth
from app.core.config import settings

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.include_router(health.router, prefix="/api")

app.include_router(auth.router, prefix="/api")   # 新增这一行
