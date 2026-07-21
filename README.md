# AEGIS-LEGION — Cloud Threat Detection & Incident Response Platform

> **Real-time threat detection, automated incident response, and ML-powered anomaly analysis — built for modern cloud infrastructure.**

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Prerequisites](#prerequisites)
5. [Local Development Setup](#local-development-setup)
6. [Production Deployment](#production-deployment)
7. [Agent Installation](#agent-installation)
8. [API Reference](#api-reference)
9. [Authentication & Authorization](#authentication--authorization)
10. [Rule Engine](#rule-engine)
11. [ML Anomaly Detection](#ml-anomaly-detection)
12. [Real-Time Communication (SSE)](#real-time-communication-sse)
13. [Notification System](#notification-system)
14. [Multi-Tenancy](#multi-tenancy)
15. [Database Schema](#database-schema)
16. [Environment Variables](#environment-variables)
17. [Security Considerations](#security-considerations)
18. [Troubleshooting](#troubleshooting)

---

## Overview

AEGIS-LEGION is a full-stack cloud security operations platform that monitors servers, detects threats in real-time, and provides an integrated incident response workflow. It consists of three core components:

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend API** | FastAPI (Python) | REST API, event ingestion, rule engine, ML pipeline |
| **Frontend Dashboard** | React + Vite | Real-time SOC dashboard, incident management, chat |
| **Server Agent** | Python (psutil) | Lightweight daemon deployed on monitored servers |

### Data Flow

```
[Server Agent] --HTTP/API Key--> [Ingest API] --> [Rule Engine] --> [Incident DB]
                                      |                |                 |
                                      v                v                 v
                                 [ML Detector]   [Broadcaster]   [Dashboard UI]
                                                  (SSE Push)
```

---

## Architecture

```
ctdirp_scaffold_fastapi/
├── agent/                          # Deployable server agent
│   └── agent.py                    # Heartbeat + threat simulation daemon
├── cloud-threat-detection-platform/
│   └── backend/
│       └── src/
│           ├── auth/               # JWT + password hashing (security.py, permissions.py)
│           ├── core/               # Rate limiter (SlowAPI)
│           ├── database.py         # SQLAlchemy engine + session factory
│           ├── detection/          # ML model definitions
│           ├── models/             # ORM models (User, Incident, Rule, Server, etc.)
│           ├── routes/             # API endpoints (auth, ingest, incidents, rules, servers)
│           ├── schemas/            # Pydantic request/response schemas
│           ├── services/           # Business logic layer
│           │   ├── anomaly_detector.py   # Isolation Forest ML engine
│           │   ├── broadcaster.py        # SSE pub/sub system
│           │   ├── email_service.py      # Templated email (Jinja2)
│           │   ├── notification_service.py # SMTP / Resend / Slack integrations
│           │   └── rule_engine.py        # Condition matching + incident creation
│           └── templates/          # HTML email templates (Jinja2)
├── frontend/
│   └── src/
│       ├── components/             # React components (19 total)
│       ├── context/                # AuthContext (JWT state management)
│       ├── styles.css              # Global design system + responsive utilities
│       └── App.jsx                 # Router (react-router-dom)
```

---

## Technology Stack

### Backend

| Technology | Version | Purpose | Why This Choice |
|-----------|---------|---------|-----------------|
| **FastAPI** | 0.100+ | REST API framework | Async-native, automatic OpenAPI docs, dependency injection. Significantly faster than Flask/Django for real-time workloads. |
| **SQLAlchemy** | 2.0 | ORM + database abstraction | Industry-standard Python ORM. Supports SQLite (dev) and PostgreSQL (prod) with zero code changes. |
| **PostgreSQL** | 14+ | Production database | ACID-compliant, handles concurrent writes from multiple agents. Scales horizontally with read replicas. |
| **SQLite** | 3.x | Local development database | Zero-config, file-based. Ideal for single-developer iteration without running a DB server. |
| **python-jose** | 3.3+ | JWT token creation/verification | Lightweight, industry-standard. Used for stateless auth. |
| **passlib** | 1.7+ | Password hashing | Secure, configurable context with multiple algorithm support. |
| **scikit-learn** | 1.3+ | ML anomaly detection (Isolation Forest) | Production-grade, minimal dependencies. Isolation Forest excels at unsupervised anomaly detection with small sample sizes. |
| **joblib** | 1.3+ | ML model persistence | Efficient serialization of trained scikit-learn models to disk. |
| **SlowAPI** | 0.1+ | Rate limiting | Prevents DoS on critical endpoints. Configurable per-route limits. |
| **Jinja2** | 3.x | Email HTML templating | Server-side rendering for branded welcome and alert emails. |
| **Resend** | API v1 | Transactional email delivery | Modern API-based email. Fallback to raw SMTP for self-hosted deployments. |
| **Kafka** *(optional)* | 3.x | Event streaming (disabled by default) | For high-throughput deployments. Events are processed synchronously by default (direct mode). |

### Frontend

| Technology | Version | Purpose | Why This Choice |
|-----------|---------|---------|-----------------|
| **React** | 18+ | UI framework | Component-based architecture, massive ecosystem. Ideal for real-time dashboards with frequent state updates. |
| **Vite** | 5+ | Build tool + dev server | 10-100x faster HMR than Webpack. Near-instant hot reloads during development. |
| **react-router-dom** | 6+ | Client-side routing | Declarative routing with protected route wrappers for auth-gated pages. |
| **axios** | 1.x | HTTP client | Promise-based, interceptor support for automatic JWT attachment. |
| **Chart.js / react-chartjs-2** | 4+ | Data visualization | Lightweight charting for threat trend timelines. |
| **Vanilla CSS** | — | Styling | Full control over the cyberpunk design system. Custom CSS variables, media queries, and animations without framework overhead. |

### Agent

| Technology | Purpose |
|-----------|---------|
| **psutil** | Cross-platform system metrics (CPU, RAM, disk I/O, network, processes) |
| **requests** | HTTP client for API communication |
| **threading** | Concurrent heartbeat (10s) and threat monitoring (1s) loops |

---

## Prerequisites

- **Python** 3.10+
- **Node.js** 18+ and **npm** 9+
- **PostgreSQL** 14+ *(production)* or SQLite *(local development)*
- **Git** 2.x

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/timi83/AEGIS-LEGION.git
cd AEGIS-LEGION
```

### 2. Backend Setup

```bash
cd cloud-threat-detection-platform/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set required environment variables
export JWT_SECRET="your-secret-key-here"
export DATABASE_URL="sqlite:///../../ctdirp.db"  # SQLite for local dev

# Start the backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure API endpoint
echo "VITE_API_URL=http://localhost:8000" > .env

# Start the dev server
npm run dev
```

The dashboard will be available at `http://localhost:5173`.

### 4. Create Your First Account

Navigate to `http://localhost:5173/register` and create your account. Registering a new organization provisions its initial administrator. In production, gate who can create organizations (invite-only or approval) rather than leaving registration fully open.

---

## Production Deployment

### Recommended Stack

| Service | Provider | Notes |
|---------|----------|-------|
| Backend API | **Render** / **Railway** / **AWS ECS** | Set `DATABASE_URL` to your PostgreSQL connection string |
| Frontend | **Vercel** / **Netlify** | Set `VITE_API_URL` to your deployed backend URL |
| Database | **Neon** / **Supabase** / **RDS** | PostgreSQL 14+ recommended |
| Agent | Any Linux/Windows server | Runs as a background service (systemd/nssm) |

### Backend Environment (Production)

```env
JWT_SECRET=<strong-random-string>
DATABASE_URL=postgresql://user:pass@host:5432/ctdirp_db
RESEND_API_KEY=re_xxxxxxxxxxxx       # For email alerts
SLACK_WEBHOOK_URL=https://hooks.slack.com/...  # Optional
FRONTEND_URL=https://your-frontend.vercel.app
```

---

## Agent Installation

The agent is a single Python script that runs on any server you want to monitor.

### Quick Start

```bash
# 1. Copy agent.py to the target server
scp agent/agent.py user@server:/opt/aegis-agent/

# 2. Install dependencies
pip install psutil requests

# 3. Configure
export AGENT_API_URL="https://your-backend.com/api"
export AGENT_API_KEY="your-generated-api-key"

# 4. Run
python agent.py
```

### What the Agent Sends

The agent runs two concurrent threads:

| Thread | Interval | Data Sent |
|--------|----------|-----------|
| **Heartbeat** | Every 10 seconds | CPU %, RAM %, disk I/O (MB/s), network I/O (MB/s), process count, top CPU process, active network connections, OS info, IP address |
| **Monitor** | Every 1 second | Simulated threat events (login failures, malware detection) at configurable probabilities |

### Running as a Service (Linux)

Run the agent under a dedicated, unprivileged service account — **never as root**. If the agent host or its API key is compromised, the blast radius is limited to that low-privilege account.

```bash
# Create a locked-down system user for the agent (no login, no home shell)
sudo useradd --system --no-create-home --shell /usr/sbin/nologin aegis-agent
```

```ini
# /etc/systemd/system/aegis-agent.service
[Unit]
Description=AEGIS-LEGION Server Agent
After=network.target

[Service]
Type=simple
User=aegis-agent
# Keep the API key out of the unit file — read it from a root-owned,
# 0600 environment file instead of inlining it here.
EnvironmentFile=/etc/aegis-agent/agent.env
ExecStart=/usr/bin/python3 /opt/aegis-agent/agent.py
Restart=always
RestartSec=5
# Hardening
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

```bash
# /etc/aegis-agent/agent.env  (root-owned, chmod 600)
# AGENT_API_URL=https://your-backend.com/api
# AGENT_API_KEY=your-generated-api-key

sudo systemctl enable aegis-agent
sudo systemctl start aegis-agent
```

---

## API Reference

### Authentication

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `POST /api/register` | POST | None | Create a new user account |
| `POST /api/token` | POST | None | OAuth2 login, returns JWT |
| `GET /api/me` | GET | JWT | Get current user profile |
| `PUT /api/me` | PUT | JWT | Update username/full name |
| `POST /api/generate-api-key` | POST | JWT | Generate API key for agent auth |
| `PUT /api/organization` | PUT | JWT (Admin) | Rename organization |

### Event Ingestion

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `POST /api/ingest/` | POST | API Key or JWT | Ingest a security event (rate limited) |

**Request Body:**
```json
{
  "source": "hostname",
  "event_type": "system_heartbeat",
  "details": "CPU at 95%",
  "severity": "low",
  "data": {
    "cpu": 95.2,
    "ram": 67.1,
    "disk_write_mb": 12.5,
    "net_out_mb": 0.8
  }
}
```

### Incidents

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `GET /api/incidents/` | GET | JWT | List all incidents (org-scoped) |
| `GET /api/incidents/{id}` | GET | JWT | Get single incident |
| `DELETE /api/incidents/{id}` | DELETE | JWT | Delete incident |
| `PUT /api/incidents/{id}/update-status` | PUT | JWT | Change status (open/investigating/mitigated/resolved/closed) |
| `POST /api/incidents/{id}/assign` | POST | JWT | Assign users to incident |
| `GET /api/incidents/{id}/notes` | GET | JWT | Get chat/investigation notes |
| `POST /api/incidents/{id}/notes` | POST | JWT | Post a note (supports @mentions) |
| `GET /api/incidents/{id}/candidates` | GET | JWT | List eligible assignees |

### Rules

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `GET /api/rules/` | GET | JWT | List all rules (org-scoped) |
| `POST /api/rules/` | POST | JWT | Create a detection rule |
| `DELETE /api/rules/{id}` | DELETE | JWT | Delete a rule |

### Servers

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `GET /api/servers/` | GET | JWT | List all registered servers |
| `PUT /api/servers/{id}` | PUT | JWT | Rename a server |
| `DELETE /api/servers/{id}` | DELETE | JWT (Admin) | Remove a server |
| `GET /api/servers/agent/download` | GET | None | Download the agent script |

### Real-Time Stream

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `GET /api/stream` | GET (SSE) | JWT | Server-Sent Events stream for live dashboard updates |

---

## Authentication & Authorization

### Dual Authentication

The platform supports two authentication methods:

1. **JWT Bearer Token** — Used by the dashboard UI. Tokens have a configurable expiry.
2. **X-API-Key Header** — Used by server agents. Keys are generated per-user via the Settings page.

### Role-Based Access Control (RBAC)

| Role | Permissions |
|------|-------------|
| **Admin** | Full access. Manage users, assign incidents to anyone, rename org, manage server access, view all org incidents. |
| **Analyst** | View assigned server incidents, self-assign ("Take") unassigned incidents, post investigation notes. |
| **Viewer** | Read-only access to incidents. Cannot post notes or modify assignments. |

---

## Rule Engine

The rule engine processes every ingested event against user-defined rules. Rules support dot-notation field access and four operators.

### Condition Matching

| Operator | Meaning |
|----------|---------|
| `equals` | Exact string match on a field |
| `contains` | Substring match on a field |
| `gt` | Greater than (numeric) |
| `lt` | Less than (numeric) |

Conditions reference event fields by dot-notation path and are combined per rule. Build and tune your own rules from the Rules page; the specific fields, thresholds, and built-in fallbacks are intentionally not enumerated here.

### Processing Logic

1. **DB Rules First**: Fetches enabled rules scoped to the event's organization. Targeted rules (server-specific) are evaluated before global rules.
2. **Incident Merge**: If an open incident already exists for the same source + event type, the alert is merged (alert count incremented, severity escalated if warranted).
3. **Fallback Rules**: If no user-defined DB rules exist, built-in fallback rules handle known critical event types automatically.

---

## ML Anomaly Detection

### Algorithm: Isolation Forest

The platform uses scikit-learn's `IsolationForest` for unsupervised anomaly detection on server telemetry.

### Feature Vector

The detector scores a multi-dimensional vector derived from host telemetry — compute, memory, and I/O signals reported by the agent heartbeat. The exact features and weighting are part of the detection model and are not documented publicly.

### Lifecycle

1. **Training Phase**: The detector buffers an initial set of heartbeat events to learn "normal" behavior.
2. **Pending Approval**: After training, the model enters a dormant state until an admin approves it (anti-data-poisoning measure).
3. **Active Inference**: Once approved, the model scores every heartbeat. Anomalies trigger an alert event that feeds back into the rule engine.
4. **Reset**: Admins can reset the model to force retraining (useful after infrastructure changes).

### Multi-Tenant Isolation

Each `(organization_id, server_hostname)` pair gets its own independent model. Models are persisted per org+server; for multi-instance deployments, back them with shared/durable storage so model state stays consistent across replicas.

---

## Real-Time Communication (SSE)

The platform uses **Server-Sent Events (SSE)** for real-time dashboard updates. This is lighter than WebSockets and works through corporate proxies and load balancers.

### Event Types Broadcast

| Event Type | Trigger | Payload |
|------------|---------|---------|
| `event` | New event ingested | Event data + rule match results |
| `status_update` | Incident status changed | Incident ID + new status |
| `note_added` | New chat message/system log | Note content + author + timestamp |
| `assignment_update` | User assigned to incident | Incident ID + updated assignee list |

### Architecture

```
[Backend Route] --> broadcaster.publish(event)
                         |
                         v
              [asyncio.Queue per subscriber]
                         |
                         v
              [SSE /api/stream endpoint]
                         |
                         v
              [Frontend EventSource listener]
```

---

## Notification System

### Channels

| Channel | Configuration | Use Case |
|---------|--------------|----------|
| **Resend API** | `RESEND_API_KEY` | Primary email delivery (API-based, no SMTP ports needed) |
| **SMTP** | `ALERT_EMAIL_FROM`, `ALERT_EMAIL_PASSWORD` | Fallback email via Gmail/custom SMTP |
| **Slack** | `SLACK_WEBHOOK_URL` | Team channel alerts |
| **In-App** | Notification model in DB | Bell icon notifications via @mentions |

### Email Templates

| Template | Trigger |
|----------|---------|
| Welcome Email | New user registration |
| API Key Confirmation | Key generation |
| Admin Alert (New User) | User joins organization |
| Critical Threat Alert | High/Critical incident created |
| Password Reset | Reset request |

---

## Multi-Tenancy

AEGIS-LEGION is fully multi-tenant. Data isolation is enforced at the database query level:

- **Organizations**: Each user belongs to an organization. All data (incidents, rules, servers, ML models) is scoped to the organization.
- **Server Access Control**: Admins can assign specific servers to specific analysts, restricting their incident visibility to only those servers.
- **Rule Isolation**: Rules created by Org A are never evaluated against events from Org B.
- **ML Model Isolation**: Each org+server combination trains its own independent model.

---

## Database Schema

```
┌──────────────┐     ┌──────────────────┐     ┌──────────────┐
│ organizations│     │      users       │     │   servers    │
├──────────────┤     ├──────────────────┤     ├──────────────┤
│ id (PK)      │◄────│ organization_id  │     │ id (PK)      │
│ name         │     │ id (PK)          │◄────│ user_id (FK) │
└──────────────┘     │ username         │     │ hostname     │
                     │ email            │     │ ip_address   │
                     │ hashed_password  │     │ os_info      │
                     │ role             │     │ status       │
                     │ api_key          │     │ last_heartbeat│
                     └────────┬─────────┘     └──────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
    ┌─────────▼────┐  ┌──────▼───────┐  ┌────▼──────────┐
    │  incidents   │  │    rules     │  │ incident_notes│
    ├──────────────┤  ├──────────────┤  ├───────────────┤
    │ id (PK)      │  │ id (PK)      │  │ id (PK)       │
    │ user_id (FK) │  │ user_id (FK) │  │ incident_id   │
    │ org_id (FK)  │  │ org_id (FK)  │  │ user_id (FK)  │
    │ org_incident_│  │ name         │  │ content       │
    │   id         │  │ conditions   │  │ is_system_log │
    │ title        │  │ severity     │  │ timestamp     │
    │ severity     │  │ target_server│  └───────────────┘
    │ status       │  │ enabled      │
    │ source       │  └──────────────┘
    │ alert_count  │
    │ timestamp    │
    └──────────────┘
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET` | **Yes** | — | Secret key for JWT signing. **Must be set or backend refuses to start.** |
| `DATABASE_URL` | **Yes** | `postgresql://...` | Database connection string. Use `sqlite:///path.db` for local dev. |
| `VITE_API_URL` | **Yes** (Frontend) | — | Backend API base URL (e.g., `https://api.example.com`) |
| `RESEND_API_KEY` | No | — | Resend API key for email delivery |
| `ALERT_EMAIL_FROM` | No | — | SMTP sender email address |
| `ALERT_EMAIL_PASSWORD` | No | — | SMTP sender password / app password |
| `ALERT_EMAIL_SMTP` | No | `smtp.gmail.com` | SMTP server hostname |
| `ALERT_EMAIL_PORT` | No | `587` | SMTP port (587 for TLS, 465 for SSL) |
| `SLACK_WEBHOOK_URL` | No | — | Slack incoming webhook URL |
| `KAFKA_ENABLED` | No | `false` | Enable Kafka event streaming |
| `KAFKA_BOOTSTRAP_SERVERS` | No | `localhost:9092` | Kafka broker address |
| `FRONTEND_URL` | No | `http://localhost:5173` | Used in email links |
| `AGENT_API_URL` | No (Agent) | `https://your-backend.com/api` | Backend URL for agent |
| `AGENT_API_KEY` | **Yes** (Agent) | — | API key generated from Settings page |

---

## Security Considerations

1. **JWT Secret**: The backend **refuses to start** if `JWT_SECRET` is not set. This is intentional — it prevents running with a default/empty secret. Use a long, random value and rotate it if it may have been exposed.
2. **Password Hashing**: Passwords are salted and hashed via passlib's `CryptContext` and length-validated before hashing. Standardizing on a slow, modern algorithm (bcrypt/argon2) as the sole scheme is recommended.
3. **Rate Limiting**: Applied to selected endpoints (e.g., event ingestion) to blunt abuse. Authentication endpoints should additionally be throttled and paired with account lockout — verify this is configured before exposing the API publicly.
4. **ML Data Poisoning Protection**: Trained ML models enter a "Pending Approval" state. An admin must explicitly approve the model before it begins active inference.
5. **API Key Authentication**: Agent API keys are generated server-side with secure random generation and can be rotated at any time. Treat them as secrets — scope issuance and store/transmit them accordingly.
6. **Access Control**: Incident, rule, server, and ML data is organization-scoped at the query level, and role checks gate sensitive actions (user and server management, assignment, note posting). Authorization is enforced server-side; review it as part of any deployment.
7. **Secrets & Data Files**: `.env`, `*.db`, and `*.sqlite` are git-ignored to prevent accidental exposure. Never commit real credentials — configure them via environment variables or a secrets manager.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Backend crashes on start | Missing `JWT_SECRET` | Set the `JWT_SECRET` environment variable |
| Agent returns `401` | Invalid or missing API key | Generate a new key in Settings → API Access |
| No incidents appearing | No rules defined | Create rules in the Rules page, or check fallback rule conditions |
| ML model stuck in "Training" | Insufficient heartbeats received | Wait for the agent to send enough heartbeat events (check ML Monitor for progress) |
| Emails not sending | Missing `RESEND_API_KEY` or SMTP credentials | Configure at least one email provider in environment variables |
| Frontend can't reach backend | Wrong `VITE_API_URL` | Verify the URL in `frontend/.env` matches your running backend |

---

## License

This project is proprietary. All rights reserved.

---

*Built with precision by Abioye Timileyin .C. Every line of code, from the ML pipeline to the CSS animations, was crafted by Timileyin.*
