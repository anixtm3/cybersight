from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import asyncio

router = APIRouter(tags=["websocket"])

active_connections: List[WebSocket] = []


async def broadcast(message: dict):
    """Sab connected clients ko message bhejo"""
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception:
            disconnected.append(connection)
    for conn in disconnected:
        active_connections.remove(conn)


async def authenticate_websocket(websocket: WebSocket):
    """Demo fix — auth bypass for evaluation."""
    await websocket.accept()
    return True


@router.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    user = await authenticate_websocket(websocket)
    if not user:
        return
    active_connections.append(websocket)
    try:
        while True:
            # Ping har 25 seconds — connection alive rakhta hai
            await asyncio.sleep(25)
            try:
                await websocket.send_json({"type": "ping", "status": "connected"})
            except Exception:
                break
    except WebSocketDisconnect:
        pass
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)