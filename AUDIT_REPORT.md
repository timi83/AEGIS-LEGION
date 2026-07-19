# CTDIRP / AEGIS LEGION — Complete Software Audit Report

**Subject:** Cloud Threat Detection & Incident Response Platform (CTDIRP), branded "AEGIS LEGION"
**Repository:** `ctdirp_scaffold_fastapi`
**Audit date:** 2026-07-19
**Auditor role:** Principal Architect / Principal Security Engineer / Senior QA / DevOps / Performance / Product
**Assessment context:** Pre-production launch readiness for a multi-tenant SaaS intended for thousands of users
**Methodology:** Full manual source inspection of all first-party code (backend FastAPI, React frontend, DevOps, tests, docs). Every finding below was verified against a specific file and line; nothing is assumed.

---

## 0. Executive Verdict (read this first)

**This platform is NOT production ready.** It is a functional, feature-rich prototype with genuinely interesting capabilities (multi-tenant threat rules, per-tenant Isolation-Forest ML, live SSE incident feed, agent-based telemetry). However, it contains **at least three confirmed cross-tenant data-isolation defects** that break the core security promise of a multi-tenant SaaS, a **downgraded password-hashing scheme**, **no rate limiting on authentication**, **live credentials sitting in the working tree**, and an enormous amount of debug/throwaway code committed to the repository. For a security product — where the buyer's entire reason for purchase is that you handle isolation and secrets correctly — these are launch-blocking.

| Dimension | Score /100 | Grade |
|---|---|---|
| Security | 22 | F |
| Architecture | 45 | D |
| Maintainability | 30 | F |
| Performance & Scalability | 38 | D |
| Testing | 40 | D |
| Documentation | 55 | C |
| UX / Frontend | 62 | C |
| DevOps / Operability | 35 | F |
| **Overall** | **38** | **F (Not production ready)** |

**Top 5 launch blockers:**
1. Cross-tenant IDOR on `/api/incidents/{id}` (read, delete, status, notes) — any org can touch any other org's incidents.
2. Global SSE broadcaster leaks every tenant's live incident stream to every connected user.
3. Password hashing silently downgraded to `sha256_crypt` (fast hash) as the default scheme.
4. No rate limiting / brute-force protection on `/api/token` login or `/api/forgot-password`.
5. Live SMTP app password and Telegram bot token present in `backend/.env` in the working tree; weak default `JWT_SECRET`.

---

## 1. Project Overview

### 1.1 Purpose
A multi-tenant **Cloud Threat Detection & Incident Response Platform**. Organizations register, deploy a lightweight Python **agent** (`backend/static/agent.py`) onto their servers, and the agent streams heartbeats and security events to the backend. The backend runs a **rule engine** and a per-tenant **Isolation-Forest ML anomaly detector**, generates **incidents**, supports **incident triage** (assignment, notes/chat, @mentions, status workflow), and pushes **live updates** to the dashboard via Server-Sent Events. Notifications go out via email (SMTP/Resend), Slack, and Telegram.

### 1.2 Technology Stack

| Layer | Technology | Evidence |
|---|---|---|
| Backend framework | FastAPI (Starlette) | `backend/main.py` |
| ORM / DB access | SQLAlchemy (declarative, sync) | `backend/src/database.py` |
| Database | PostgreSQL 15 (prod); SQLite fallback + tests | `docker-compose.yml`, `database.py:9` |
| Auth | OAuth2 password flow, JWT (`python-jose`), passlib | `src/auth/security.py`, `src/routes/auth.py` |
| Streaming/eventing | Kafka (optional, `KAFKA_ENABLED`), in-proc SSE broadcaster | `main.py:137`, `src/services/broadcaster.py` |
| ML | scikit-learn IsolationForest, joblib persistence | `src/services/anomaly_detector.py` |
| Rate limiting | slowapi | `src/core/limiter.py` |
| Email | smtplib + Resend HTTP API, Jinja2 templates | `src/services/notification_service.py`, `email_service.py` |
| Frontend | React 18 + Vite, React Router, axios, Tailwind | `frontend/package.json`, `frontend/vite.config.js` |
| Frontend auth state | JWT in `localStorage`, `jwt-decode` | `frontend/src/context/AuthContext.jsx` |
| Reverse proxy | Nginx (SPA + `/api` proxy) | `frontend/nginx.conf` |
| Deploy targets | Docker Compose (local), Render (`aegis-legion.onrender.com`), Vercel (frontend) | `agent.py:15`, `main.py:77` |

### 1.3 External services & providers
Gmail SMTP, Resend, Slack webhooks, Telegram Bot API, Render (backend host), Vercel (frontend host), optional MongoDB & Kafka & Zookeeper (declared in compose, largely unused in "Direct Mode").

### 1.4 Deployment model
Split deployment: React static build on Vercel → talks to FastAPI backend on Render. Docker Compose exists for a full local stack (Postgres, Kafka, Zookeeper, Mongo, backend, frontend/nginx). Note the compose backend is **dev-mode** (`--log-level debug`, source bind-mounted, single uvicorn process).

---

## 2. Repository Structure Review

### 2.1 Layout confusion (architectural smell — High)
There are **two overlapping project roots**:
- `cloud-threat-detection-platform/backend/` and `cloud-threat-detection-platform/frontend/` (the latter contains only `package-lock.json`)
- top-level `frontend/` (the *actual* frontend) and top-level `scripts/`, `agent/`

The backend Dockerfile builds from the repo root and copies `cloud-threat-detection-platform/backend/`, while the compose file uses `context: ./backend`. This duplication makes it ambiguous which tree is authoritative and is a frequent source of "works in compose, breaks on Render" drift. **Consolidate to a single, unambiguous monorepo layout.**

### 2.2 Massive committed throwaway code (High)
**87 tracked scripts** match `debug_/reset_/seed_/migrate_/verify_/check_/force_/nuclear_/drop_/fix_` naming. Examples: `backend/reset_plain.py`, `backend/set_plain_password.py`, `backend/force_reset_admin.py`, `scripts/nuclear_reset.py`, `scripts/reset_prod_db.py`, `backend/debug_verify_password.py`, `backend/test_plaintext_verify.py`. These are one-off operational hacks, not product code. Several are dangerous if ever run against prod (`reset_prod_db.py`, `nuclear_reset.py`). They inflate the attack surface, confuse new engineers, and several manipulate passwords in plaintext.

### 2.3 Committed binary/stale artifacts (Medium)
`backend/model_isolation_forest.pkl` and `model_isolation_forest_v2.pkl` are tracked ML pickles. Pickles are code-execution vectors if ever loaded from an untrusted source, and they are stale relative to the runtime path (`models/model_org_*.pkl`). Remove from VCS.

### 2.4 Dead/duplicated code inside modules (Medium)
- `src/routes/incidents.py` `get_all_incidents` runs the same query twice (lines 82–84) and returns the same dict twice; `alert_count` key is duplicated in every serializer (lines 95–96, 123–124).
- `create_incident_note` has an unreachable second `return` (line 316) and a duplicate `db.commit(); db.refresh()` (lines 284–288).
- `main.py` has duplicated comment markers ("Force reload for DB init fix" ×2) and a commented duplicate router include (line 59).
- `servers.py` `ServerResponse` and `HeartbeatSchema` duplicate `cpu_usage`/`ram_usage`/`cpu` fields.

### 2.5 Naming/consistency
Legacy `organization` (string) coexists with relational `organization_id` on `User`, `Incident`, `Rule`. Both are kept "in sync" manually (e.g. `auth.py:324`). This dual source of truth is a data-integrity hazard (see §7).

---

## 3. Functional Audit (feature-by-feature)

| Feature | Implemented? | Notes / gaps |
|---|---|---|
| Org self-registration (first user = admin) | Yes | `auth.py:61`. No email verification; org name uniqueness is case-sensitive (`WidgetCo` ≠ `widgetco`). |
| Login (JWT) | Yes | `auth.py:247`. 30-min fixed expiry, no refresh, no lockout. |
| Admin user management (create/list/delete) | Yes | Org-scoped. Delete does manual cascade via raw SQL (`auth.py:199`). |
| Password reset (forgot/reset by token) | Yes | `auth.py:441`. Reset token = JWT `type=password_reset`, 15 min. See §4.6 token-type confusion. |
| Admin resets sub-user password | Yes | `auth.py:411`. Cannot reset another admin. |
| API key generation (for agents) | Yes | Any role incl. viewer can mint `sk_live_...`; stored plaintext (`auth.py:329`). |
| Server inventory / heartbeat | Yes | `servers.py:116`, `ingest.py:117`. |
| Rule engine (DB rules + fallbacks) | Yes | `rule_engine.py`. Casing bug in dedup (`status=="Open"` vs "open"). |
| Per-tenant ML anomaly detection | Partial | Works in-process; **not persisted across replicas/restarts consistently** (§8.5). |
| Incident lifecycle (create/list/get/status/delete) | Yes | **IDOR on get/delete/status (§4.4).** |
| Incident notes / chat + @mentions | Yes | Viewers blocked from posting; note read has **no access check** (`incidents.py:194`). |
| Incident assignment (self + admin multi) | Yes | Reasonable RBAC, but relies on fragile string parsing (`_parse_assignment_input`). |
| Notifications (in-app bell) | Yes | Correctly user-scoped (`notifications.py`). |
| Live updates (SSE) | Yes | **Global broadcast — cross-tenant leak (§4.5).** |
| Email/Slack/Telegram alerts | Partial | Email path heavily instrumented with debug probes; Telegram configured but no send path wired for incidents. |
| Audit log | Yes | Admin sees org logs, user sees own. |
| MFA | **No** | Not implemented. |
| Email verification | **No** | Not implemented. |

---

## 4. Authentication & Authorization Audit

### 4.1 Password hashing downgraded — **CRITICAL**
`src/auth/security.py:20`:
```python
pwd_context = CryptContext(schemes=["sha256_crypt", "bcrypt"], deprecated="auto")
```
Because `sha256_crypt` is listed **first**, passlib uses it as the **default scheme for all newly hashed passwords** (registration, resets, admin-set). The inline comment ("NUCLEAR OPTION: Switching to sha256_crypt because bcrypt is incorrectly crashing on length checks in Docker") reveals this was a workaround for the well-known passlib×bcrypt 4.x incompatibility. `sha256_crypt` is a fast hash relative to bcrypt/argon2 and is a materially weaker choice for password-at-rest storage; an attacker who exfiltrates the DB can crack passwords far faster than the product implies.
**Fix:** Pin `bcrypt<4.1` (or move to `argon2`), restore `schemes=["bcrypt"]` / `["argon2"]`, keep `sha256_crypt` only as a deprecated verifier for migration. Effort: **S**.

### 4.2 No brute-force protection on login — **HIGH**
`/api/token` (`auth.py:247`) and `/api/forgot-password` (`auth.py:441`) have **no `@limiter.limit`**. Only `/api/ingest` is rate-limited (`ingest.py:88`). Credential-stuffing and password-spray are unthrottled. **Fix:** add slowapi limits (e.g. `5/minute` per IP + per-account backoff) to auth endpoints. Effort: **S**.

### 4.3 Deactivated users still authenticate — **Medium**
`get_current_user` (`auth.py:27`) validates the JWT and loads the user but **never checks `user.is_active`**. Setting `is_active=False` does not revoke access. There is also no token revocation/blocklist, so a stolen 30-minute token cannot be killed. **Fix:** check `is_active`; consider short access token + refresh + server-side revocation list. Effort: **S–M**.

### 4.4 Cross-tenant IDOR on incidents — **CRITICAL**
In `src/routes/incidents.py`, these handlers fetch by primary key **with no organization or ownership filter**:
- `get_incident` (line 110): `db.query(Incident).filter(Incident.id == incident_id).first()`
- `delete_incident` (line 131): same — **any authenticated user can delete any incident in the system**.
- `update_incident_status` (line 142): same — cross-org status tampering.
- `get_incident_notes` (line 194): explicit `# TODO: strict RBAC` — returns note content for any incident id.
- `create_incident_note` (line 213): only checks the incident exists, not that the caller's org owns it — you can post notes and trigger @mention notifications into another org's incident.

A user in Org A can enumerate `GET /api/incidents/1..N`, read Org B's incident details/notes, flip statuses, and delete them. This is a textbook Broken Access Control / IDOR and, for a security product, is disqualifying.
**Fix:** every by-id incident handler must filter/verify `Incident.organization_id == current_user.organization_id` (plus per-role server-scope checks matching `get_all_incidents`). Add cross-org negative tests. Effort: **M**.

### 4.5 SSE stream leaks all tenants' events — **HIGH**
`src/services/broadcaster.py` is a single global pub/sub: `publish()` pushes each event to **every** subscriber queue with no tenant key. `ingest.py` (line 221) and `incidents.py` (lines 166–184, 299) broadcast incident payloads (id, title, severity, status, note content, assignees) globally. Any authenticated user of any org who opens `GET /api/events/stream` receives **live incident data from all organizations**. The code even acknowledges the risk in a comment ("Security risk if we send private notifs to public stream"). **Fix:** partition the broadcaster by `organization_id` (subscribe with the user's org, publish with the event's org) and filter server-side. Effort: **M**.

### 4.6 Reset-token can be used as a session token — **Medium**
`create_access_token` for password reset embeds `{"sub": email, "type": "password_reset"}` (`auth.py:454`). `get_current_user` (`auth.py:33`) decodes any token with a valid `sub` and **does not check `type`**. A leaked reset link's token (valid 15 min) is therefore usable as a full API bearer token. **Fix:** require `type` absent/`access` in `get_current_user`; give reset tokens a dedicated audience. Effort: **S**.

### 4.7 SSE token in query string — **Medium**
`events.py:41` takes the JWT as a URL query param (`?token=`). Query strings land in nginx `access_log` (`nginx.conf:5` logs to stdout), browser history, and proxy logs. **Fix:** pass via header or short-lived one-time SSE ticket. Effort: **S**.

### 4.8 API keys: broad issuance + plaintext storage — **Medium**
Any role (including `viewer`) can call `/api/generate-api-key` (`auth.py:329`), and keys are stored **unhashed** in `users.api_key` (`user.py:22`). DB read = full agent impersonation. **Fix:** restrict issuance to admin/analyst; store only a hash of the key; show plaintext once. Effort: **M**.

### 4.9 Positives
- Backend refuses to boot without `JWT_SECRET` (`security.py:9`) — good fail-closed behavior.
- RBAC dependency (`RoleChecker`, `admin_only`) is clean and correctly applied to user-management and server-delete endpoints; RBAC is covered by tests (`test_rbac.py`).
- `forgot-password` does not reveal account existence (`auth.py:445`).
- Org-scoped filtering *is* correctly done for rules (`rules.py:56,74`), notifications, and list endpoints — proving the team knows the pattern; it's just applied inconsistently.

---

## 5. Security Audit (OWASP Top 10)

| # | Category | Severity | Finding |
|---|---|---|---|
| A01 | Broken Access Control | **Critical** | Incident IDOR (§4.4); SSE cross-tenant leak (§4.5); `get_incident_notes` no auth check; `/incidents/debug/assignment-check` (`incidents.py:566`) lets any user enumerate all org usernames/ids. |
| A02 | Cryptographic Failures | **Critical** | `sha256_crypt` default (§4.1); weak default `JWT_SECRET=supersecretjwtkey_change_this` in `.env`; API keys stored plaintext. |
| A03 | Injection | Low | SQLAlchemy ORM + parameterized `text(... :uid)` used throughout — no SQLi found. `ilike(f"%{event_type}%")` interpolates into a *parameterized* LIKE, so not injectable, but attacker-controlled `%`/`_` can distort rule dedup matching. No XSS sinks in the API; React escapes by default. |
| A04 | Insecure Design | High | Dual `organization`/`organization_id` model; global mutable ML singleton; no email verification; reset-token reuse as access token. |
| A05 | Security Misconfiguration | High | CORS regex `https://aegis-legion-.*\.vercel\.app` (any attacker-registered matching preview host) + `allow_methods=["*"]`, `allow_headers=["*"]`; nginx `error_log ... debug`; no security headers (no CSP, HSTS, X-Frame-Options, X-Content-Type-Options); compose runs backend in debug with source mounted; Postgres exposed on host `5432` with password `password`. |
| A06 | Vulnerable/Outdated Components | Medium | Unpinned backend deps (`requirements.txt` mostly version-less) → non-reproducible builds; `bcrypt 3.2.2` vendored; `passlib` unmaintained. No SCA/CVE gating. |
| A07 | Identification & Auth Failures | High | No login rate limiting (§4.2); no MFA; no account lockout; `is_active` not enforced; 30-min token, no revocation. |
| A08 | Software & Data Integrity | Medium | Tracked `.pkl` pickles (deserialization risk if source trust ever slips); no CI, no signed builds; ad-hoc `ALTER TABLE` at startup instead of migrations. |
| A09 | Logging & Monitoring Failures | High | Pervasive `print()` of sensitive context (login `username` at `auth.py:249`, `get_db` debug prints, event bodies in rule engine); no structured logging, no alerting, no audit of the IDOR-prone endpoints; `test_plaintext_verify.py`/`set_plain_password.py` indicate plaintext-password handling existed. |
| A10 | SSRF | Low | No user-controlled outbound URL fetch reachable by tenants. Slack webhook is admin-config only. |

### 5.1 Secrets exposure — **Critical (operational)**
`backend/.env` is present in the working tree with **real-looking live credentials**:
- `ALERT_EMAIL_PASSWORD="aiwavdkbholyrfef"` (Gmail app password)
- `TELEGRAM_BOT_TOKEN=8589880808:AAG...H5GFYw`
- `JWT_SECRET=supersecretjwtkey_change_this` (weak, guessable)
- `POSTGRES_PASSWORD=password`

Good news: `git ls-files` confirms `.env` is **not committed** (gitignored). But the file exists locally and these secrets have almost certainly been shared alongside the code. **Treat all of them as compromised: rotate the Gmail app password, revoke/rotate the Telegram bot token, generate a 256-bit random `JWT_SECRET`, and change the DB password.** Effort: **S** (but urgent).

### 5.2 DoS protections (partial positives)
`ContentSizeLimitMiddleware` (`main.py:29`) caps bodies at 50 KB, and `/ingest` is rate-limited. However the size check reads only the `Content-Length` header and can be bypassed with chunked transfer encoding, and slowapi keys on `get_remote_address` which, behind Render/Vercel proxies, may resolve to the proxy IP unless `X-Forwarded-For` is trusted — meaning the limiter could throttle all users as one bucket or be evadable. **Fix:** enforce a streaming size cap and configure trusted-proxy client IP resolution.

---

## 6. API Audit

- **Auth/authorization:** mostly enforced via `Depends(get_current_user)` / `admin_only`; gaps are the IDOR endpoints (§4.4) and the debug endpoints.
- **Validation:** Pydantic models used for most bodies. But `create_incident` (`incidents.py:16`) takes `title/description/severity/status` as **query parameters**, not a body (confirmed by `test_incidents.py:16` using `params=`), which is poor REST hygiene and pushes data into logs. Several handlers accept raw `payload: dict` (`create_incident_note`, `assign_incident`) with no schema, so inputs are unvalidated.
- **Status codes:** generally reasonable (401/403/404/409), but many handlers wrap failures as `HTTPException(500, detail=str(e))`, **leaking internal exception text to clients** (e.g. `auth.py:127,162,243`, `incidents.py:106`).
- **Consistency:** response shapes are hand-built dicts, not response models, so field drift is likely. `alert_count` duplicated in serializers.
- **Pagination/filtering/sorting:** **absent.** `GET /api/incidents/`, `/api/audit-logs`, `/api/servers` return *all* rows unbounded → O(n) payloads and memory pressure at scale (§8).
- **Idempotency:** ingest generates an `event_id` but incidents are deduped by fragile `ilike` title/description matching, not by `event_id` (which is `unique` on the model but unused in the merge path).
- **Documentation:** FastAPI auto-generates `/docs`; no curated OpenAPI descriptions, no examples, no auth documented for the SSE query-token pattern.

---

## 7. Database Audit

- **Schema management:** No Alembic migrations despite `alembic` in requirements. Tables are created via `Base.metadata.create_all` and a raw `ALTER TABLE rules ADD COLUMN target_server` executed **on every startup** (`main.py:131`), swallowing exceptions. Dozens of manual `scripts/migrate_*.py` do the rest. This is not reproducible and will diverge across environments. **High.**
- **Dual tenancy columns:** `organization` (string) + `organization_id` (FK) both live on `User`/`Incident`/`Rule` and are manually kept in sync (`auth.py:324`). Queries mix them (`incidents.py:46` filters by `User.organization` string; `rules.py:56` by `organization_id`). A rename that half-fails leaves tenants partially cross-linked. **High — normalize to `organization_id` only.**
- **Constraints/indexes:** `username` deliberately non-unique (`user.py:11`); `email` unique; `incidents.event_id` unique but unused for dedup; reasonable indexes on FK/scoping columns. Missing composite index for `(organization_id, org_incident_id)` used in the "next friendly id" hot path.
- **Referential integrity:** deletes rely on **manual raw-SQL cascade** (`auth.py:199-243`) rather than `ON DELETE CASCADE`. Any new child table will silently break user deletion. **Medium.**
- **Concurrency:** `org_incident_id` is computed as `max()+1` with no lock/unique constraint (`incidents.py:21`, `rule_engine.py:105`) → duplicate friendly IDs under concurrent ingestion. **Medium.**
- **Backups:** none defined. Postgres volume only. **High for prod.**

---

## 8. Performance & Scalability Audit

### 8.1 Backend concurrency model
Sync SQLAlchemy + sync route handlers on FastAPI. The Dockerfile CMD runs a **single uvicorn process** (`Dockerfile:17`) — `gunicorn` is in requirements but not used. Blocking DB calls in async routes (`ingest.py`, `incidents.py` mix `async def` with sync ORM) can stall the event loop. **Under load this is a hard ceiling.**

### 8.2 Unbounded queries
No pagination anywhere (§6). `GET /api/incidents/` loads all org incidents plus assignee relations per row (N+1 via `i.assignees`). At 10k+ incidents per tenant this is multi-MB JSON and heavy DB load per dashboard poll.

### 8.3 Synchronous processing in request path
`/ingest` runs the rule engine and ML inference **inline** (`ingest.py:147,179`), then broadcasts. Heartbeat also runs rules + ML **twice** in places. Every agent heartbeat does DB writes + model predict on the request thread. Thousands of agents → thousands of synchronous ML calls. Kafka exists precisely to offload this but defaults to disabled (`KAFKA_ENABLED != true`).

### 8.4 Debug logging cost
`print(...)` on nearly every request path (`get_db` prints twice per request, rule engine prints per rule/condition). At scale this is significant I/O and log volume, and leaks data.

### 8.5 ML state is not horizontally scalable — **High**
`OrganizationMLManager` is an **in-process singleton** holding detectors in a Python dict, with models on **local disk** (`models/model_org_*.pkl`). With multiple replicas (the only way to scale on Render/K8s), each instance has its own divergent buffers/models; "approve" on one replica doesn't apply to others; container restart loses training buffers. The ML feature effectively assumes a single, sticky, long-lived process. **Redesign for shared state (object store for models, external buffer, or a dedicated ML worker).**

### 8.6 SSE fan-out
Global broadcaster with per-subscriber `asyncio.Queue` in one process — again single-process bound and, as noted, cross-tenant. Won't survive multi-replica without a shared bus (Redis pub/sub, etc.).

### Scalability readiness estimate
| Scale | Verdict |
|---|---|
| 100 users | Works (single instance). |
| 1,000 users | Degraded — unbounded lists, sync ML per heartbeat, debug logging. |
| 10,000 users | Fails without pagination, async offload, and multi-replica-safe ML/SSE. |
| 100,000 users | Not achievable on current architecture. |

---

## 9. Frontend Quality Audit

Strengths: a real, multi-component React app (Dashboard, Rules, IncidentModal, MLMonitor, mobile overhaul per git log, Tailwind, landing page, activity feed, threat-trend chart). Routing is guarded by `ProtectedRoute`.

Weaknesses:
- **Token in `localStorage`** (`AuthContext.jsx:8`) → any XSS = token theft; no `HttpOnly` cookie option. **Medium.**
- **No CSP** and no security headers from nginx → XSS blast radius is large. **Medium.**
- **No silent token refresh**; 30-min hard expiry means abrupt logout mid-work (`AuthContext` logs out on 401). **UX/Medium.**
- `ProtectedRoute` only checks token presence, not role — role gating is server-side only (acceptable, but the UI can render admin controls to non-admins that then 403).
- Bundle/perf not profiled here; `frontend/package-lock.json` exists in two places (root and `cloud-threat-detection-platform/frontend/`) — dependency drift risk.

(Full a11y/responsive testing requires a running build; not executed. Landing/dashboard components suggest reasonable structure but were not WCAG-audited. Treat §10 as not-yet-verified rather than passing.)

---

## 10. Accessibility Audit
**Not verifiable from source alone** (needs a rendered build + axe/Lighthouse). Flag as an open task: verify semantic landmarks, form label associations, focus management in modals (`IncidentModal`, `ProfileModal`, `ServerAccessModal`), keyboard traps, and color contrast on the dark theme before claiming WCAG 2.1 AA.

---

## 11. Code Quality Audit

- **DRY/KISS:** repeatedly violated — duplicated queries/returns (`incidents.py`), duplicated model fields, two `get_db` implementations (`database.py` and `rules.py:15`), copy-pasted ML-anomaly blocks in `ingest.py` and `servers.py`.
- **Complexity:** `assign_incident` and `process_event` are long, branchy, and contain the developer's stream-of-consciousness comments ("Let's assume ADDITIVE for now…", "I should just fire the broadcast…"). These read as unedited AI/pair output left in place.
- **Magic values:** severity level maps, thresholds (`ANOMALY_THRESHOLD=-0.6`, `TRAINING_BUFFER_SIZE=100`) hardcoded; status casing inconsistent ("Open" vs "open") causing real dedup bugs.
- **Error handling:** broad `except:` swallows (e.g. `ingest.py:79 try/except: pass` on JWT), and `str(e)` leaked to clients.
- **Typing:** partial. Pydantic on some, raw `dict` on others.
- **Comments:** many are apologies/uncertainty or dead code, not intent — a maintainability tax.

---

## 12. AI-Generated Code Review
Strong signals of unedited AI assistance: emoji-laden logs, narrator comments debating design mid-function, "NUCLEAR OPTION" workaround comment, duplicated statements from repeated regenerations, `debug/`-prefixed diagnostic endpoints shipped in the router, and 87 throwaway scripts. Areas needing **human refactoring before launch**: incident access control (§4.4), broadcaster tenancy (§4.5), ML state model (§8.5), tenancy data model (§7), and removal of all debug/print/throwaway code.

---

## 13. Testing Audit
A real pytest suite exists (`backend/tests/`, ~680 lines): `test_auth`, `test_incidents`, `test_ingest`, `test_rbac`, `test_rules`, `test_servers`, `test_sse`, with good fixtures (org/admin/analyst/viewer, in-memory SQLite). RBAC and assignment flows are covered.

Gaps (**the tests would pass while the product is exploitable**):
- **Zero cross-tenant/negative isolation tests.** All fixtures share one org, so the IDOR (§4.4) and SSE leak (§4.5) are invisible to the suite. This is the single most important missing test class.
- No tests for password-reset token misuse, `is_active` enforcement, login rate limiting, or API-key scoping.
- No frontend tests at all.
- No coverage measurement, no CI to run any of it (§14).
- ML detector, notification service, and email paths untested.

---

## 14. DevOps Audit
- **CI/CD: none.** No `.github/workflows`, no pipeline. Nothing runs tests, lint, or SCA before deploy.
- **Docker:** backend image runs as **root**, single process, no healthcheck; compose is dev-configured (debug log, bind mount, exposed Postgres with weak creds). Two Dockerfiles with mismatched build contexts (`Dockerfile` copies `cloud-threat-detection-platform/backend`, compose uses `./backend`).
- **Config:** relies on `.env`; no secrets manager; `ALLOWED_ORIGINS_REGEX` defaults to a permissive Vercel pattern.
- **Observability:** `print`/`logging.basicConfig(INFO)` only; no metrics, tracing, error tracking, or alerting. Log files (`backend_logs.txt`, `startup.log`, `debug_rules*.log`, `nginx_debug.log`) are committed to the tree.
- **Rollback/backup:** no strategy defined.
- **Health:** `/health` and `/api/health` exist (good), but no container-level healthcheck wires them.

---

## 15. Dependency Audit
- Backend `requirements.txt`: **mostly unpinned** (`fastapi`, `sqlalchemy`, `uvicorn[standard]`, `scikit-learn`, etc.) → non-reproducible, and the exact bug the team hit (passlib×bcrypt) is a direct symptom of not pinning. Pin everything; add `pip-audit`/Dependabot.
- `passlib` is effectively unmaintained; combined with the sha256_crypt workaround this is a liability — plan a move to `argon2-cffi`.
- `kafka-python`, `pymongo`(implied by Mongo service), `alembic` are declared/deployed but largely unused → dead weight and extra CVE surface.
- Frontend: duplicate lockfiles; run `npm audit` and dedupe to one frontend root.

---

## 16. Scalability Summary
Covered in §8. Net: acceptable for a pilot/single-instance demo; **not** ready for multi-replica scale until pagination, async/offloaded processing, multi-replica-safe ML, and a shared event bus are in place.

---

## 17. Business Logic Audit
- **Incident dedup/merge** hinges on `status == "Open"` plus `ilike` on title/description (`rule_engine.py:31`) while incidents can be created as `"open"`/`"investigating"`/`"closed"` — casing/format mismatches silently create duplicates or fail to merge. **Medium.**
- **Severity override** logic is sound but only applies on merge, not on create.
- **Friendly `org_incident_id`** race (§7) can produce duplicate human-facing IDs.
- **@mention/@everyone** notification targeting is org-scoped correctly, but `create_incident_note` doesn't verify the caller can access the incident's org (ties back to §4.4).
- **ML approval gate** (anti-poisoning) is a nice idea but undermined by non-persistent multi-replica state (§8.5).

---

## 18. Documentation Audit
Positives: multiple READMEs, `PRODUCT_INFO.md/html`, product PDF, `.env` is well-commented, agent has usage docs. A prior commit even redacted sensitive docs. Gaps: no architecture doc reconciling the two project roots, no API reference beyond auto-`/docs`, no deployment runbook covering Render/Vercel env vars, no threat model, no data-retention/backup docs. Documentation currently **overstates** security posture relative to the code.

---

## 19. Production Readiness Assessment
**Not production ready.** Blockers below must be closed before any real-user launch.

**Launch blockers (must fix):**
1. Incident IDOR — org-scope every by-id incident handler (§4.4).
2. SSE cross-tenant leak — tenant-partition the broadcaster (§4.5).
3. Restore strong password hashing (bcrypt/argon2) and re-hash on next login (§4.1).
4. Rate-limit `/token` and `/forgot-password`; add lockout (§4.2).
5. Rotate all exposed secrets; generate strong `JWT_SECRET`; remove `.env` from any shared artifact (§5.1).
6. Remove debug endpoints (`/incidents/debug/*`, `/api/debug/*`) and all `print()` of sensitive data (§4, §5 A09).
7. Enforce `is_active` and separate reset-token from access-token (§4.3, §4.6).
8. Add security headers/CSP at nginx; tighten CORS regex and methods/headers (§5 A05).

---

## 20. Risk Register (ranked)

| ID | Severity | Finding | Business impact | Technical impact | Fix | Effort |
|---|---|---|---|---|---|---|
| R1 | Critical | Incident IDOR (`incidents.py` get/delete/status/notes) | Total loss of tenant confidentiality/integrity; breach-notification event | Cross-org read/delete/modify | Org-scope all by-id handlers + negative tests | M |
| R2 | Critical | Password hashing = sha256_crypt (`security.py:20`) | Faster credential cracking after any DB leak | Weak hashes at rest | Pin bcrypt<4.1/argon2; migrate | S |
| R3 | Critical | Live secrets in `.env` + weak JWT secret | Account/email/bot takeover; token forgery | Full auth compromise | Rotate + 256-bit secret + secrets mgr | S (urgent) |
| R4 | High | Global SSE broadcaster leak (`broadcaster.py`) | Real-time cross-tenant data exposure | Confidentiality breach | Partition by org | M |
| R5 | High | No login rate limiting | Account takeover via brute force | Auth failure | slowapi + lockout | S |
| R6 | High | No CI, unpinned deps, no SCA | Ships regressions/CVEs unnoticed | Supply-chain/quality risk | GitHub Actions + pin + pip-audit | M |
| R7 | High | ML/SSE single-process, local pkl | Feature breaks on scale-out | No horizontal scaling | Shared state/bus | L |
| R8 | High | Dual tenancy columns / no migrations | Data corruption, drift | Integrity risk | Normalize + Alembic | M |
| R9 | Medium | API keys plaintext + any-role issuance | Agent impersonation on DB leak | AuthN weakness | Hash keys; restrict issuance | M |
| R10 | Medium | Reset token usable as session token | Session hijack via reset link | AuthZ gap | Check token `type` | S |
| R11 | Medium | No pagination on list endpoints | Slow dashboards, DoS-by-data | Performance | Add limit/offset/cursor | M |
| R12 | Medium | Debug endpoints + print logging | Info disclosure, log leakage | Exposure | Remove; structured logging | S |
| R13 | Medium | CORS regex + `*` methods/headers; no security headers | XSS/clickjacking/abuse | Misconfig | Tighten + CSP/HSTS/XFO | S |
| R14 | Medium | No `is_active` / token revocation | Can't offboard/kill sessions | AuthN gap | Enforce + revocation list | S–M |
| R15 | Medium | Manual cascade deletes; friendly-id race | Orphans/dup IDs | Integrity | FK cascade + unique constraint | M |
| R16 | Low | Tracked pkl/logs/throwaway scripts | Repo hygiene, deserialization | Maintainability | Purge from VCS | S |
| R17 | Low | Incident status casing dedup bug | Duplicate/missed incidents | Logic | Normalize status enum | S |

Effort key: S ≤ 1 day, M ≈ 2–5 days, L > 1 week.

---

## 21. Executive Dashboard

```
┌──────────────────────────────────────────────────────────────┐
│  CTDIRP / AEGIS LEGION — PRODUCTION READINESS SCORECARD        │
├───────────────────────────────┬──────────┬───────────────────┤
│  Dimension                    │  Score   │  Grade            │
├───────────────────────────────┼──────────┼───────────────────┤
│  Security                     │   22/100 │   F                │
│  Architecture                 │   45/100 │   D                │
│  Maintainability              │   30/100 │   F                │
│  Performance & Scalability    │   38/100 │   D                │
│  Testing                      │   40/100 │   D                │
│  Documentation                │   55/100 │   C                │
│  UX / Frontend                │   62/100 │   C                │
│  DevOps / Operability         │   35/100 │   F                │
├───────────────────────────────┼──────────┼───────────────────┤
│  OVERALL                      │   38/100 │   F                │
│  PRODUCTION READY?            │   NO — 8 launch blockers open  │
└───────────────────────────────┴──────────┴───────────────────┘
```

---

## 22. Prioritized Action Plan

**Immediate (before ANY real user — days, not weeks):**
1. Rotate the Gmail app password, Telegram bot token, DB password; set a 256-bit random `JWT_SECRET`. (R3)
2. Org-scope all incident by-id handlers; add cross-tenant negative tests. (R1)
3. Restore bcrypt/argon2 hashing (pin `bcrypt<4.1`), keep sha256_crypt as verify-only. (R2)
4. Partition the SSE broadcaster by organization. (R4)
5. Rate-limit `/token` and `/forgot-password`; add lockout. (R5)
6. Delete debug endpoints and sensitive `print()`s; enforce `is_active`; separate reset-token type. (R12, R14, R10)
7. Add nginx security headers + CSP; tighten CORS. (R13)

**High priority (first 2–4 weeks):**
8. Introduce GitHub Actions CI: tests + `pip-audit`/`npm audit` + lint, pin all deps. (R6)
9. Adopt Alembic; normalize tenancy to `organization_id`; add FK cascades + unique `(org_id, org_incident_id)`. (R8, R15)
10. Add pagination/cursors to list endpoints; hash API keys and restrict issuance. (R11, R9)
11. Move ingest rule/ML processing off the request path (Kafka worker or task queue). (R7)

**Medium priority:**
12. Re-architect ML/SSE for multi-replica (shared model store + Redis pub/sub). (R7)
13. Consolidate the repo to one root; purge tracked pkl/logs/throwaway scripts. (R16)
14. Structured logging + error tracking (Sentry) + container healthchecks + backup policy.
15. Frontend: move token to HttpOnly cookie or add silent refresh; add frontend tests; run WCAG audit.

**Long-term technical debt:**
16. Replace passlib with argon2; formal threat model; data-retention policy; load/perf testing at 10k agents; MFA and email verification.

**Quick wins (high value, low effort):**
- Remove duplicate statements in `incidents.py` (§2.4).
- Fix status casing to a single enum (R17).
- Add `is_active` check (one line, closes offboarding gap).
- Pin dependencies (prevents recurrence of the bcrypt breakage).

---

### Closing note
The product has a compelling feature set and the team clearly understands the *right* patterns — org-scoping, RBAC dependencies, rate limiting, anti-poisoning gates all appear somewhere in the code. The problem is **consistency and discipline**: the correct controls are applied to some endpoints and forgotten on others, and a large volume of debug/prototype code shipped alongside. Closing the eight launch blockers in §19 would move this from "F / not ready" to a credible beta; the High/Medium items then get it to a defensible production posture. For a security product, none of the Critical items are optional.
