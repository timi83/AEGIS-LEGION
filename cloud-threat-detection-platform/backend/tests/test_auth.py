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
async def test_rename_notifies_tagged_user_who_never_posted(
    client: httpx.AsyncClient, db_session, admin_headers, test_admin, test_analyst
):
    """
    A user who was only @-mentioned in a shared incident (never posted their own
    note) must still be notified when a co-participant renames. This matches the
    'once you have been tagged in a chat' intent.
    """
    from src.models.incident import Incident
    from src.models.incident_note import IncidentNote
    from src.models.notification import Notification

    incident = Incident(
        title="Tag thread", description="x", severity="low", status="Open",
        user_id=test_admin.id, organization_id=test_admin.organization_id,
    )
    db_session.add(incident)
    db_session.commit()
    db_session.refresh(incident)

    # Only the admin posts — and tags the analyst. The analyst never posts.
    db_session.add(IncidentNote(
        incident_id=incident.id, user_id=test_admin.id,
        content=f"@{test_analyst.username} please take a look",
    ))
    db_session.commit()

    old_name = test_admin.username
    resp = await client.put("/api/me/profile", json={"username": "Renamed Admin"}, headers=admin_headers)
    assert resp.status_code == 200

    notifs = db_session.query(Notification).filter(Notification.user_id == test_analyst.id).all()
    assert len(notifs) == 1
    assert notifs[0].message == f"{old_name} has changed their profile name to Renamed Admin"


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
async def test_login_upgrades_legacy_hash_to_bcrypt(client: httpx.AsyncClient, db_session, test_org):
    """A pre-existing sha256_crypt hash verifies on login and is transparently
    re-hashed to bcrypt — no forced password reset."""
    from passlib.context import CryptContext
    from src.models.user import User

    legacy_ctx = CryptContext(schemes=["sha256_crypt"])
    user = User(
        username="legacy_user",
        email="legacy@test.com",
        organization=test_org.name,
        organization_id=test_org.id,
        role="admin",
        hashed_password=legacy_ctx.hash("legacypass123"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    assert user.hashed_password.startswith("$5$")  # sha256_crypt

    resp = await client.post(
        "/api/token",
        data={"username": "legacy@test.com", "password": "legacypass123"},
    )
    assert resp.status_code == 200

    db_session.refresh(user)
    assert user.hashed_password.startswith("$2")  # upgraded to bcrypt


@pytest.mark.asyncio
async def test_password_reset_flow(client: httpx.AsyncClient, db_session, test_admin):
    """A valid reset token sets a new password: the new one logs in, the old one no longer does."""
    from datetime import timedelta
    from src.auth.security import create_access_token

    # Same token forgot-password issues.
    token = create_access_token({"sub": test_admin.email, "type": "password_reset"},
                                expires_delta=timedelta(minutes=15))

    resp = await client.post("/api/reset-password", json={"token": token, "new_password": "brandNewPass123"})
    assert resp.status_code == 200

    # New password works.
    ok = await client.post("/api/token", data={"username": test_admin.email, "password": "brandNewPass123"})
    assert ok.status_code == 200 and "access_token" in ok.json()

    # Old password is dead.
    old = await client.post("/api/token", data={"username": test_admin.email, "password": "adminpassword123"})
    assert old.status_code == 401


@pytest.mark.asyncio
async def test_reset_rejects_non_reset_token(client: httpx.AsyncClient, test_admin):
    """A normal login token (no type=password_reset) can't be used to reset a password."""
    from src.auth.security import create_access_token
    token = create_access_token({"sub": test_admin.email})  # no reset type
    resp = await client.post("/api/reset-password", json={"token": token, "new_password": "whatever123"})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_forgot_password_no_user_enumeration(client: httpx.AsyncClient, test_admin):
    """forgot-password returns the same response whether or not the email exists."""
    r1 = await client.post("/api/forgot-password", json={"email": test_admin.email})
    r2 = await client.post("/api/forgot-password", json={"email": "nobody@nowhere.test"})
    assert r1.status_code == 200 and r2.status_code == 200
    assert r1.json() == r2.json()


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


@pytest.mark.asyncio
async def test_password_reset_token_rejected_as_session(client: httpx.AsyncClient, test_admin):
    """A password-reset token must not be usable as an API bearer token."""
    from datetime import timedelta
    from src.auth.security import create_access_token

    reset_token = create_access_token(
        data={"sub": test_admin.email, "type": "password_reset"},
        expires_delta=timedelta(minutes=15),
    )
    resp = await client.get("/api/me", headers={"Authorization": f"Bearer {reset_token}"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_deactivated_user_cannot_authenticate(client: httpx.AsyncClient, db_session, test_admin, admin_headers):
    """Setting is_active=False revokes access even with a valid token."""
    # Valid while active.
    assert (await client.get("/api/me", headers=admin_headers)).status_code == 200

    test_admin.is_active = False
    db_session.commit()

    assert (await client.get("/api/me", headers=admin_headers)).status_code == 401
