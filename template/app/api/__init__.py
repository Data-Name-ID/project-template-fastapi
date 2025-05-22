from fastapi import APIRouter

from app.api.ping.views import router as ping_router
from app.api.users.views.auth import router as auth_router

router = APIRouter(prefix="/api")

router.include_router(ping_router)
router.include_router(auth_router)
