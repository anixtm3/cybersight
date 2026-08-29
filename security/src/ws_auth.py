from fastapi import WebSocket
from rbac import get_current_user_from_token


async def authenticate_websocket(websocket: WebSocket):
    await websocket.accept()

    try:
        first_message = await websocket.receive_json()
    except Exception:
        await websocket.close(code=4001, reason="Missing or malformed token message")
        return None

    token = first_message.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return None

    try:
        user = get_current_user_from_token(token)
        return user
    except Exception:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return None