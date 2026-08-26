from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter(tags=["websocket"])

# Connected clients list
active_connections: List[WebSocket] = []


async def broadcast(message: dict):
    """Sab connected clients ko message bhejo"""
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception:
            disconnected.append(connection)
    
    # Dead connections remove karo
    for conn in disconnected:
        active_connections.remove(conn)


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Client se message wait karo (ping/pong)
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)