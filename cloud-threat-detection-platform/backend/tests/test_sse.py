import pytest
import httpx
import asyncio
from fastapi import Request, HTTPException
from fastapi.responses import StreamingResponse
from src.routes.events import stream
from src.services.broadcaster import broadcaster

@pytest.mark.asyncio
async def test_sse_stream_unauthorized(client: httpx.AsyncClient):
    # Try to connect with an invalid token using standard HTTP client
    response = await client.get("/api/events/stream?token=invalid_token_123")
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Authentication"

@pytest.mark.asyncio
async def test_sse_stream_connection_established(db_session, admin_token):
    # Construct a mock Starlette Request scope
    req = Request(scope={"type": "http", "method": "GET", "path": "/api/events/stream"})
    
    # Directly invoke the stream route function with a valid token
    response = await stream(request=req, token=admin_token, db=db_session)
    
    # Verify a StreamingResponse was successfully constructed and returned
    assert isinstance(response, StreamingResponse)
    assert response.media_type == "text/event-stream"

@pytest.mark.asyncio
async def test_sse_stream_connection_established_invalid_token(db_session):
    req = Request(scope={"type": "http", "method": "GET", "path": "/api/events/stream"})
    
    # Directly invoke with an invalid token and assert 401 HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await stream(request=req, token="invalid_token_123", db=db_session)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid Authentication"

@pytest.mark.asyncio
async def test_broadcaster_pub_sub():
    # Test the broadcaster's core logic directly to avoid client-generator race conditions
    sid, queue = await broadcaster.subscribe()
    try:
        test_event = {"event_type": "ssh_login", "details": "Successful root login from 10.0.0.5"}
        
        # Publish to all subscribers
        await broadcaster.publish(test_event)
        
        # Verify event was received in the queue
        event_received = await asyncio.wait_for(queue.get(), timeout=1.0)
        assert event_received["event_type"] == "ssh_login"
        assert event_received["details"] == "Successful root login from 10.0.0.5"
    finally:
        await broadcaster.unsubscribe(sid)


