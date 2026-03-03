from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from services import manager
import jwt
from core.config import SECRET_KEY, ALGORITHM
router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # MUST manually read JWT from query parameters
    token = websocket.query_params.get("token")

    # Reject if no token
    if not token:
        await websocket.close(code=4001)
        return

    # Decode manually (middleware doesn't work for WebSockets)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload["user_id"]
    except:
        await websocket.close(code=4002)
        return

    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            # Echo if needed, or ignore
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)
