from fastapi import APIRouter

from app.api.ping.schemas import PingPublic

router = APIRouter(prefix="/ping", tags=["Пинг"])


@router.get(
    "",
    summary="Проверка ответа севера",
    response_description="Успешный ответ",
)
async def ping() -> PingPublic:
    return PingPublic()
