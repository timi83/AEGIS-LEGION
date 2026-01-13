# backend/src/routes/events.py
from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
import asyncio
import json
from src.services.broadcaster import broadcaster
from src.routes.auth import get_current_user
from src.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/events", tags=["Events"])

async def event_generator(request: Request, token: str):
    """
    Generator that yields Server-Sent Events.
    Requires valid token.
    """
    # Verify token manually since this is a generator, 
    # but we can also do it in the route before yielding.
    # The route handler below handles the auth check.
    
    sid, queue = await broadcaster.subscribe()
    try:
        while True:
            # If client disconnected, exit
            if await request.is_disconnected():
                break
            try:
                event = await asyncio.wait_for(queue.get(), timeout=15.0)
                # SSE format: data: <json>\n\n
                yield f"data: {json.dumps(event)}\n\n"
            except asyncio.TimeoutError:
                # keep the connection alive with a ping comment
                yield ": ping\n\n"
    finally:
        await broadcaster.unsubscribe(sid)

@router.get("/stream")
async def stream(
    request: Request, 
    token: str = Query(..., description="JWT Token for authentication"),
    db: Session = Depends(get_db)
):
    # Validate User
    try:
        user = get_current_user(token, db)
        # Optional: Check if user is active/authorized (already done by get_current_user)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid Authentication")

    return StreamingResponse(event_generator(request, token), media_type="text/event-stream")
