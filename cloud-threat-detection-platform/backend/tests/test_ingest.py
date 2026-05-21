import pytest
import httpx
from src.models.server import Server

@pytest.mark.asyncio
async def test_ingest_event_success(client: httpx.AsyncClient, admin_headers):
    payload = {
        "source": "web-server-01",
        "event_type": "login_failed",
        "details": "User admin failed to log in",
        "severity": "low",
        "data": {"fail_count": 1}
    }
    response = await client.post("/api/ingest/", json=payload, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["message"] == "Event ingested successfully"
    assert "event_id" in data

@pytest.mark.asyncio
async def test_ingest_event_unauthorized(client: httpx.AsyncClient):
    payload = {
        "source": "web-server-01",
        "event_type": "login_failed",
        "details": "User admin failed to log in",
        "severity": "low",
        "data": {"fail_count": 1}
    }
    response = await client.post("/api/ingest/", json=payload)
    assert response.status_code == 401
    assert "Missing or Invalid Authentication" in response.json()["detail"]

@pytest.mark.asyncio
async def test_ingest_heartbeat_registers_server(client: httpx.AsyncClient, admin_headers, db_session, test_admin):
    # Ensure no server exists initially
    initial_servers = db_session.query(Server).filter(Server.user_id == test_admin.id).all()
    assert len(initial_servers) == 0

    payload = {
        "source": "db-server-99",
        "event_type": "system_heartbeat",
        "details": "Periodic system heartbeat",
        "severity": "low",
        "data": {"ip": "192.168.1.99", "os": "Ubuntu 22.04 LTS"}
    }
    response = await client.post("/api/ingest/", json=payload, headers=admin_headers)
    assert response.status_code == 200

    # Verify server is registered
    servers = db_session.query(Server).filter(Server.user_id == test_admin.id).all()
    assert len(servers) == 1
    assert servers[0].hostname == "db-server-99"
    assert servers[0].status == "online"
    assert servers[0].ip_address == "192.168.1.99"
    assert servers[0].os_info == "Ubuntu 22.04 LTS"
