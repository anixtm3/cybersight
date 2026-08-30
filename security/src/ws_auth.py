from fastapi import WebSocket
from app.auth_core import get_user_from_raw_token
from app.database import SessionLocal


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

    db = SessionLocal()
    try:
        user = get_user_from_raw_token(db, token)
        return user
    except Exception:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return None
    finally:
        db.close()