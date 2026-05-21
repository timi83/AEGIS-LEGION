import pytest
import httpx
from src.models.incident import Incident
from src.models.incident_note import IncidentNote
from src.models.notification import Notification

@pytest.mark.asyncio
async def test_create_incident_api(client: httpx.AsyncClient, admin_headers):
    # Query parameters are used for incident creation
    params = {
        "title": "Unauthorized Access Detected",
        "description": "Critical web-server-01 alert",
        "severity": "critical",
        "status": "open"
    }
    response = await client.post("/api/incidents/", params=params, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Incident created successfully"
    assert "id" in data

@pytest.mark.asyncio
async def test_alert_merge_into_incident(client: httpx.AsyncClient, admin_headers, db_session, test_admin):
    # Ensure no incidents exist initially
    assert db_session.query(Incident).count() == 0

    # Ingest the first login_failed brute force event (should trigger fallback rule creating a new open incident)
    payload1 = {
        "source": "host-xyz",
        "event_type": "login_failed",
        "details": "Failed attempt",
        "severity": "high",
        "data": {"fail_count": 3}
    }
    response1 = await client.post("/api/ingest/", json=payload1, headers=admin_headers)
    assert response1.status_code == 200

    # Assert incident was created
    incidents = db_session.query(Incident).all()
    assert len(incidents) == 1
    incident = incidents[0]
    assert incident.alert_count == 1
    assert "login_failed" in incident.title.lower()
    assert "host-xyz" in incident.description.lower()

    # Ingest a second matching event
    payload2 = {
        "source": "host-xyz",
        "event_type": "login_failed",
        "details": "Failed attempt 2",
        "severity": "high",
        "data": {"fail_count": 3}
    }
    response2 = await client.post("/api/ingest/", json=payload2, headers=admin_headers)
    assert response2.status_code == 200

    # Verify that no new incident was created and the existing one was updated (alert_count incremented)
    db_session.expire_all()  # Clear cache to get fresh DB states
    incidents_after = db_session.query(Incident).all()
    assert len(incidents_after) == 1
    assert incidents_after[0].id == incident.id
    assert incidents_after[0].alert_count == 2

@pytest.mark.asyncio
async def test_analyst_self_assignment(client: httpx.AsyncClient, analyst_headers, db_session, test_analyst, test_admin):
    # Create an unassigned incident first via the admin user
    incident = Incident(
        title="Unassigned Incident",
        description="No one owns this yet",
        severity="medium",
        status="Open",
        user_id=test_admin.id,
        organization_id=test_admin.organization_id
    )
    db_session.add(incident)
    db_session.commit()
    db_session.refresh(incident)

    # Let the analyst assign it to themselves ("take" it)
    payload = {"assign_to": "me"}
    response = await client.post(f"/api/incidents/{incident.id}/assign", json=payload, headers=analyst_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "You have taken this incident."

    # Verify database assignment and system note
    db_session.expire_all()
    updated_incident = db_session.query(Incident).get(incident.id)
    assert len(updated_incident.assignees) == 1
    assert updated_incident.assignees[0].id == test_analyst.id

    system_notes = db_session.query(IncidentNote).filter(IncidentNote.incident_id == incident.id).all()
    assert len(system_notes) == 1
    assert "assigned themselves" in system_notes[0].content

@pytest.mark.asyncio
async def test_admin_assigns_analyst(client: httpx.AsyncClient, admin_headers, db_session, test_admin, test_analyst):
    incident = Incident(
        title="Admin Incident",
        description="Assigned by admin",
        severity="medium",
        status="Open",
        user_id=test_admin.id,
        organization_id=test_admin.organization_id
    )
    db_session.add(incident)
    db_session.commit()
    db_session.refresh(incident)

    # Admin assigns to the analyst user
    payload = {"assign_to": f"@{test_analyst.username}"}
    response = await client.post(f"/api/incidents/{incident.id}/assign", json=payload, headers=admin_headers)
    assert response.status_code == 200
    assert "Assigned" in response.json()["message"]

    # Verify assignment
    db_session.expire_all()
    updated_incident = db_session.query(Incident).get(incident.id)
    assert len(updated_incident.assignees) == 1
    assert updated_incident.assignees[0].id == test_analyst.id

    # Verify notification log was created for the analyst
    notifications = db_session.query(Notification).filter(Notification.user_id == test_analyst.id).all()
    assert len(notifications) == 1
    assert "Assigned" in notifications[0].title
    assert "by admin_user" in notifications[0].message
