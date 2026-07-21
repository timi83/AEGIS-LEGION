import pytest
import httpx


@pytest.mark.asyncio
async def test_rename_notifies_chat_participants(
    client: httpx.AsyncClient, db_session, admin_headers, test_admin, test_analyst
):
    """
    Renaming a display name notifies co-participants of shared incident chats
    (one notification each), but not the renamer, and not unrelated users.
    """
    from src.models.incident import Incident
    from src.models.incident_note import IncidentNote
    from src.models.notification import Notification
    from src.models.user import User

    # Shared incident where BOTH admin and analyst posted a note.
    incident = Incident(
        title="Shared thread",
        description="x",
        severity="low",
        status="Open",
        user_id=test_admin.id,
        organization_id=test_admin.organization_id,
    )
    db_session.add(incident)
    db_session.commit()
    db_session.refresh(incident)

    db_session.add_all([
        IncidentNote(incident_id=incident.id, user_id=test_admin.id, content="hi"),
        IncidentNote(incident_id=incident.id, user_id=test_analyst.id, content="hey"),
    ])
    db_session.commit()

    old_name = test_admin.username

    # Admin renames themselves.
    resp = await client.put("/api/me/profile", json={"username": "Drake"}, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "Drake"

    # The co-participant (analyst) got exactly one rename notification.
    analyst_notifs = db_session.query(Notification).filter(
        Notification.user_id == test_analyst.id
    ).all()
    assert len(analyst_notifs) == 1
    assert analyst_notifs[0].message == f"{old_name} has changed their profile name to Drake"

    # The renamer did NOT notify themselves.
    self_notifs = db_session.query(Notification).filter(
        Notification.user_id == test_admin.id
    ).all()
    assert len(self_notifs) == 0


@pytest.mark.asyncio
async def test_rename_noop_sends_no_notifications(
    client: httpx.AsyncClient, db_session, admin_headers, test_admin, test_analyst
):
    """Setting the same username (or only full_name) must not notify anyone."""
    from src.models.incident import Incident
    from src.models.incident_note import IncidentNote
    from src.models.notification import Notification

    incident = Incident(
        title="Shared thread 2", description="x", severity="low", status="Open",
        user_id=test_admin.id, organization_id=test_admin.organization_id,
    )
    db_session.add(incident)
    db_session.commit()
    db_session.refresh(incident)
    db_session.add_all([
        IncidentNote(incident_id=incident.id, user_id=test_admin.id, content="hi"),
        IncidentNote(incident_id=incident.id, user_id=test_analyst.id, content="hey"),
    ])
    db_session.commit()

    # Same username -> no-op; only full_name changes.
    resp = await client.put(
        "/api/me/profile",
        json={"username": test_admin.username, "full_name": "Renamed Only"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert db_session.query(Notification).filter(
        Notification.user_id == test_analyst.id
    ).count() == 0


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
