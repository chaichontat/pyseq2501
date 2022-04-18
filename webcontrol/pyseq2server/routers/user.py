from __future__ import annotations

from logging import getLogger

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedOK

from ..api_types import UserSettings

router = APIRouter()

logger = getLogger(__name__)


@router.websocket("/user")
async def user_endpoint(ws: WebSocket) -> None:
    await ws.accept()
    try:
        while True:
            ws.app.state.user_settings = await ws.receive_json()
    except (WebSocketDisconnect, RuntimeError, ConnectionClosedOK):
        ...


@router.get("/usersettings", response_model=UserSettings)
async def get_user(request: Request) -> Request:
    return request.app.state.user_settings
