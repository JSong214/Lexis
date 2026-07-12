from fastapi import APIRouter

from app.api.v1.routes import auth, health, lessons, maimemo

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(health.router, tags=["system"])
api_router.include_router(maimemo.router, tags=["maimemo"])
api_router.include_router(lessons.router, tags=["lessons"])
