import pytest
import httpx
from src.models.server import Server

@pytest.mark.asyncio
async def test_ml_model_status_structure(client: httpx.AsyncClient, analyst_headers):
    # GET /api/servers/ml/status structure
    response = await client.get("/api/servers/ml/status", headers=analyst_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_ml_model_reset_rbac(client: httpx.AsyncClient, admin_headers, analyst_headers):
    # POST /api/servers/ml/reset (success under admin, forbidden under analyst)
    payload = {"source": "nonexistent_server"}
    
    # Analyst should be Forbidden (403)
    response = await client.post("/api/servers/ml/reset", json=payload, headers=analyst_headers)
    assert response.status_code == 403
    
    # Admin should receive 404 (Not Found) rather than 403 (Forbidden)
    response = await client.post("/api/servers/ml/reset", json=payload, headers=admin_headers)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_list_servers_rbac(client: httpx.AsyncClient, db_session, test_admin, test_analyst, admin_headers, analyst_headers):
    # 1. Create a server owned by admin
    admin_server = Server(
        hostname="admin-srv-01",
        ip_address="192.168.1.10",
        os_info="Ubuntu 22.04",
        status="online",
        user_id=test_admin.id,
        name="Admin Server"
    )
    # 2. Create a server owned by analyst
    analyst_server = Server(
        hostname="analyst-srv-01",
        ip_address="192.168.1.20",
        os_info="Ubuntu 22.04",
        status="online",
        user_id=test_analyst.id,
        name="Analyst Server"
    )
    
    db_session.add(admin_server)
    db_session.add(analyst_server)
    db_session.commit()
    
    # GET /api/servers as Admin (should see all servers in the organization)
    response_admin = await client.get("/api/servers", headers=admin_headers)
    assert response_admin.status_code == 200
    servers_admin = response_admin.json()
    assert len(servers_admin) == 2
    
    # GET /api/servers as Analyst (should only see analyst's own or assigned servers)
    response_analyst = await client.get("/api/servers", headers=analyst_headers)
    assert response_analyst.status_code == 200
    servers_analyst = response_analyst.json()
    assert len(servers_analyst) == 1
    assert servers_analyst[0]["hostname"] == "analyst-srv-01"
