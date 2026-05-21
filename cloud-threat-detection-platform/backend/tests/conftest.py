import os
os.environ["JWT_SECRET"] = "test_jwt_secret_key_123_test_jwt_secret_key_123"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["KAFKA_ENABLED"] = "false"

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import httpx

from main import app
from src.database import Base, get_db
from src.routes.rules import get_db as rules_get_db
from src.core.limiter import limiter

# Import all models to ensure they are registered on Base.metadata
from src.models.organization import Organization
from src.models.user import User
from src.models.server import Server
from src.models.incident import Incident
from src.models.rule import Rule
from src.models.audit_log import AuditLog
from src.models.incident_note import IncidentNote
from src.models.notification import Notification

from src.auth.security import get_password_hash, create_access_token

# Disable slowapi rate limits during testing to prevent failures
limiter.enabled = False

# Use SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session() -> Generator:
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables to guarantee isolation between tests
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function", autouse=True)
def override_dependencies(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[rules_get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()

import pytest_asyncio

@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="function")
def test_org(db_session):
    org = Organization(name="Test Security Org")
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org

@pytest.fixture(scope="function")
def test_admin(db_session, test_org):
    hashed_pwd = get_password_hash("adminpassword123")
    user = User(
        username="admin_user",
        email="admin@test.com",
        full_name="Admin User",
        organization=test_org.name,
        organization_id=test_org.id,
        role="admin",
        hashed_password=hashed_pwd,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_analyst(db_session, test_org):
    hashed_pwd = get_password_hash("analystpassword123")
    user = User(
        username="analyst_user",
        email="analyst@test.com",
        full_name="Analyst User",
        organization=test_org.name,
        organization_id=test_org.id,
        role="analyst",
        hashed_password=hashed_pwd,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_viewer(db_session, test_org):
    hashed_pwd = get_password_hash("viewerpassword123")
    user = User(
        username="viewer_user",
        email="viewer@test.com",
        full_name="Viewer User",
        organization=test_org.name,
        organization_id=test_org.id,
        role="viewer",
        hashed_password=hashed_pwd,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def admin_token(test_admin):
    return create_access_token(data={"sub": test_admin.email})

@pytest.fixture(scope="function")
def analyst_token(test_analyst):
    return create_access_token(data={"sub": test_analyst.email})

@pytest.fixture(scope="function")
def viewer_token(test_viewer):
    return create_access_token(data={"sub": test_viewer.email})

@pytest.fixture(scope="function")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture(scope="function")
def analyst_headers(analyst_token):
    return {"Authorization": f"Bearer {analyst_token}"}

@pytest.fixture(scope="function")
def viewer_headers(viewer_token):
    return {"Authorization": f"Bearer {viewer_token}"}
