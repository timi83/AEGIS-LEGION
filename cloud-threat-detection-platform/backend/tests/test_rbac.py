import pytest
import httpx
from src.models.user import User

@pytest.mark.asyncio
async def test_create_user_rbac(client: httpx.AsyncClient, admin_headers, analyst_headers, viewer_headers):
    # Try to create a user using POST /api/users
    payload = {
        "username": "rbac_test_user",
        "email": "rbac_test@test.com",
        "password": "password123",
        "full_name": "RBAC Test User",
        "organization": "Test Security Org",
        "role": "analyst"
    }

    # 1. Analyst should be Forbidden (403)
    response = await client.post("/api/users", json=payload, headers=analyst_headers)
    assert response.status_code == 403

    # 2. Viewer should be Forbidden (403)
    response = await client.post("/api/users", json=payload, headers=viewer_headers)
    assert response.status_code == 403

    # 3. Admin should succeed (200)
    response = await client.post("/api/users", json=payload, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "rbac_test_user"

@pytest.mark.asyncio
async def test_list_users_rbac(client: httpx.AsyncClient, admin_headers, analyst_headers, viewer_headers):
    # GET /api/users
    
    # 1. Analyst should be Forbidden (403)
    response = await client.get("/api/users", headers=analyst_headers)
    assert response.status_code == 403

    # 2. Viewer should be Forbidden (403)
    response = await client.get("/api/users", headers=viewer_headers)
    assert response.status_code == 403

    # 3. Admin should succeed (200)
    response = await client.get("/api/users", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_delete_user_rbac(client: httpx.AsyncClient, db_session, test_analyst, admin_headers, analyst_headers):
    # DELETE /api/users/{user_id}
    
    # Analyst tries to delete analyst (should be Forbidden - 403)
    response = await client.delete(f"/api/users/{test_analyst.id}", headers=analyst_headers)
    assert response.status_code == 403
