from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
# from app.ws_auth import authenticate_websocket# app/ws_auth.py — TEMPORARY LOCAL STUB, merge ke waqt Kanav ki asli file se REPLACE karna hai

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
    """PLACEHOLDER — asli implementation Kanav ke merge se aayegi."""
    await websocket.accept()
    await websocket.close(code=4001, reason="Auth not yet merged locally")
    return None