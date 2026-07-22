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
    # Subscriber receives events published to its own organization.
    sid, queue = await broadcaster.subscribe(organization_id=1)
    try:
        test_event = {"event_type": "ssh_login", "details": "Successful root login from 10.0.0.5"}
        await broadcaster.publish(test_event, organization_id=1)

        event_received = await asyncio.wait_for(queue.get(), timeout=1.0)
        assert event_received["event_type"] == "ssh_login"
        assert event_received["details"] == "Successful root login from 10.0.0.5"
    finally:
        await broadcaster.unsubscribe(sid)


@pytest.mark.asyncio
async def test_broadcaster_tenant_isolation():
    # An event for org 2 must reach org 2 subscribers only — never org 1.
    sid1, q1 = await broadcaster.subscribe(organization_id=1)
    sid2, q2 = await broadcaster.subscribe(organization_id=2)
    try:
        await broadcaster.publish({"secret": "org2-only"}, organization_id=2)

        received = await asyncio.wait_for(q2.get(), timeout=1.0)
        assert received["secret"] == "org2-only"

        # The org-1 subscriber must get nothing.
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(q1.get(), timeout=0.3)
    finally:
        await broadcaster.unsubscribe(sid1)
        await broadcaster.unsubscribe(sid2)


