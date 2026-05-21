import pytest
import httpx
from src.models.rule import Rule
from src.models.incident import Incident

@pytest.mark.asyncio
async def test_rule_crud(client: httpx.AsyncClient, admin_headers):
    # 1. Create a Rule
    payload = {
        "name": "High CPU Anomaly Rule",
        "description": "Triggers on high CPU usage",
        "conditions": [
            {"field": "data.cpu", "op": "gt", "value": "90.0"}
        ],
        "severity": "high",
        "enabled": True,
        "target_server": None
    }
    response = await client.post("/api/rules/", json=payload, headers=admin_headers)
    assert response.status_code == 200
    rule_id = response.json()["id"]
    assert response.json()["message"] == "Rule created"

    # 2. List Rules
    response_list = await client.get("/api/rules/", headers=admin_headers)
    assert response_list.status_code == 200
    rules = response_list.json()
    assert len(rules) >= 1
    assert rules[0]["name"] == "High CPU Anomaly Rule"
    assert rules[0]["id"] == rule_id

    # 3. Delete Rule
    response_delete = await client.delete(f"/api/rules/{rule_id}", headers=admin_headers)
    assert response_delete.status_code == 200
    assert response_delete.json()["message"] == "Rule deleted"

@pytest.mark.asyncio
async def test_rule_engine_evaluation(client: httpx.AsyncClient, admin_headers, db_session, test_admin):
    # Ensure no incidents or rules exist initially
    assert db_session.query(Rule).count() == 0
    assert db_session.query(Incident).count() == 0

    # 1. Create a custom rule in the DB that matches if event_type equals "unauthorized_sudo"
    # Condition format in DB is a JSON-serialized string of a list of condition dicts.
    import json
    custom_rule = Rule(
        name="Critical Unauthorized Sudo Rule",
        description="Detect sudo attempts by standard users",
        conditions=json.dumps([
            {"field": "event_type", "op": "equals", "value": "unauthorized_sudo"}
        ]),
        severity="critical",
        enabled=True,
        organization_id=test_admin.organization_id,
        organization=test_admin.organization
    )
    db_session.add(custom_rule)
    db_session.commit()

    # 2. Ingest an event that matches this rule
    payload = {
        "source": "web-01",
        "event_type": "unauthorized_sudo",
        "details": "User bob attempted to run sudo apt update",
        "severity": "low",
        "data": {}
    }
    response = await client.post("/api/ingest/", json=payload, headers=admin_headers)
    assert response.status_code == 200

    # 3. Verify that the rule engine evaluated the custom rule and created a corresponding Incident
    db_session.expire_all()
    incidents = db_session.query(Incident).all()
    assert len(incidents) == 1
    assert incidents[0].title == "Critical Unauthorized Sudo Rule"
    assert incidents[0].severity == "critical"
    assert incidents[0].source == "web-01"
