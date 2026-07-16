import asyncio
import json
import os
import threading
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Force reload for DB init fix
# Force reload for DB init fix
from fastapi import FastAPI
# Force reload for auth updates
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from kafka import KafkaConsumer
from fastapi.middleware.cors import CORSMiddleware
from src.database import init_db, get_db
from src.models import user, server, incident, rule, audit_log, incident_note, notification
from src.routes import incidents_router, rules_router, ingest_router, auth_router, servers, notifications_router
from src.routes.events import router as events_router
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from src.core.limiter import limiter
from fastapi import Request, Response

class ContentSizeLimitMiddleware:
    def __init__(self, app, max_content_length: int = 50 * 1024):
        self.app = app
        self.max_content_length = max_content_length

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
            
        headers = dict(scope.get("headers", []))
        content_length = headers.get(b"content-length")
        
        if content_length and int(content_length) > self.max_content_length:
            response = Response(content="Payload Too Large (Max 50KB)", status_code=413)
            return await response(scope, receive, send)
            
        return await self.app(scope, receive, send)
app = FastAPI(title="CTDIRP Backend")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(ingest_router, prefix="/api")
app.include_router(incidents_router, prefix="/api")
app.include_router(rules_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(events_router, prefix="/api")
app.include_router(servers.router, prefix="/api")
app.include_router(notifications_router, prefix="/api")

# Duplicate router inclusion fix
# app.include_router(servers.router, prefix="/api") 

origins = [
    "http://localhost:5173",  # Vite dev server default
    "http://127.0.0.1:5173",
    "http://localhost:3000"   # optional
]

# Production: Load allowed origins from environment variable
# Example: ALLOWED_ORIGINS="https://my-app.vercel.app,https://another-domain.com"
env_origins = os.getenv("ALLOWED_ORIGINS")
if env_origins:
    origins = [origin.strip() for origin in env_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Secured to only allowed origins (Not '*')
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(ContentSizeLimitMiddleware, max_content_length=50*1024) # 50KB limit against Memory Exhaustion DoS


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PostgreSQL connection (Docker internal hostname: db)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@db:5432/ctdirp"
).strip()

engine = create_engine(DATABASE_URL)


##############################################################
# ROUTES
##############################################################
# Routers are already included with prefix="/api" above.
# We do NOT need to include them again without prefix.
# Ensuring health check is also available via /api/health for consistency if needed,
# or just relying on root /health.


##############################################################
# KAFKA CONSUMER (BACKGROUND)
##############################################################
# Consumer logic moved to src.services.kafka_consumer

##############################################################
# STARTUP
##############################################################
@app.on_event("startup")
def startup_event():
    logger.info("⚙️ Initializing database tables...")
    try:
        init_db()
    except Exception as e:
        logger.error(f"init_db failed: {e}")
        
    # Auto-migration for new columns
    try:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE rules ADD COLUMN target_server VARCHAR(255)"))
            logger.info("✅ Added target_server column to rules table.")
    except Exception:
        logger.info("ℹ️ target_server column check (already exists)")

    # Start Kafka consumer in a background daemon thread
    if os.getenv("KAFKA_ENABLED") == "true":
        try:
            from src.services.kafka_consumer import start_consumer
            
            # Capture the main event loop to pass to the consumer thread
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            t = threading.Thread(target=start_consumer, args=(True, 20, 5, loop), daemon=True, name="kafka-consumer-thread")
            t.start()
            logger.info("🧵 Kafka consumer thread started (daemon).")
        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {e}")
    else:
        logger.info("❌ Kafka consumer DISABLED (KAFKA_ENABLED != true). Direct Mode active.")


##############################################################
# HEALTH CHECK
##############################################################
@app.get("/")
def root():
    return {"message": "CTDIRP backend running successfully!"}

@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}

# Re-expose health at /api/health for Nginx/Frontend convenience
@app.get("/api/health")
def health_check_api():
    return health_check()


##############################################################
# MANUAL EVENT PUBLISH
##############################################################
# /log_event REMOVED per security audit. Use /api/ingest


# Forced reload trigger

