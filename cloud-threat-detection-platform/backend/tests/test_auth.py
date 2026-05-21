import pytest
import httpx

@pytest.mark.asyncio
async def test_register_success(client: httpx.AsyncClient):
    payload = {
        "username": "newuser",
        "email": "new@test.com",
        "password": "securepassword",
        "full_name": "New User",
        "organization": "Brand New Org",
        "role": "admin"
    }
    response = await client.post("/api/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@test.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_register_duplicate_email(client: httpx.AsyncClient, test_admin):
    payload = {
        "username": "anotheruser",
        "email": test_admin.email,  # duplicate email
        "password": "password123",
        "full_name": "Another User",
        "organization": "Another Org",
        "role": "admin"
    }
    response = await client.post("/api/register", json=payload)
    assert response.status_code == 400
    assert "Invalid details or Organization already exists." in response.json()["detail"]

@pytest.mark.asyncio
async def test_register_duplicate_org(client: httpx.AsyncClient, test_org):
    payload = {
        "username": "anotheruser",
        "email": "another@test.com",
        "password": "password123",
        "full_name": "Another User",
        "organization": test_org.name,  # duplicate org name
        "role": "admin"
    }
    response = await client.post("/api/register", json=payload)
    assert response.status_code == 400
    assert "Invalid details or Organization already exists." in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_success(client: httpx.AsyncClient, test_admin):
    payload = {
        "username": test_admin.email,  # OAuth2 form sends email in username field
        "password": "adminpassword123"
    }
    response = await client.post("/api/token", data=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client: httpx.AsyncClient, test_admin):
    payload = {
        "username": test_admin.email,
        "password": "wrongpassword"
    }
    response = await client.post("/api/token", data=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

@pytest.mark.asyncio
async def test_read_users_me(client: httpx.AsyncClient, test_admin, admin_headers):
    response = await client.get("/api/me", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == test_admin.username
    assert data["email"] == test_admin.email

@pytest.mark.asyncio
async def test_read_users_me_unauthorized(client: httpx.AsyncClient):
    response = await client.get("/api/me")
    assert response.status_code == 401
