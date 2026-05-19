# AEGIS-LEGION — Product Information

> **The All-in-One Cloud Security Operations Platform**

---

## 1. What is AEGIS-LEGION?

AEGIS-LEGION is a **Cloud Threat Detection and Incident Response Platform (CTDIRP)** — a unified security operations center (SOC) that monitors cloud infrastructure in real-time, automatically detects threats using both rule-based and machine learning systems, and provides a complete incident response workflow with team collaboration tools.

It is a **full-stack, production-grade platform** that replaces the need for multiple disconnected security tools by combining:

- **Server Monitoring** (like Datadog/Zabbix)
- **Threat Detection** (like Splunk/SIEM)
- **Incident Management** (like PagerDuty/Opsgenie)
- **Team Communication** (like Slack threads)
- **ML Anomaly Detection** (like custom data science pipelines)

...into a single, cohesive product.

---

## 2. The Problem

### The Security Tool Sprawl Crisis

Modern organizations face a fragmented security landscape:

1. **Tool Overload**: A typical SOC uses 5-10 separate tools for monitoring, alerting, ticketing, and communication. Context is lost between handoffs.
2. **Alert Fatigue**: Security teams receive hundreds of alerts daily. Without intelligent deduplication, analysts waste time on duplicate notifications for the same underlying issue.
3. **Slow Response Times**: When a threat is detected in Tool A, the analyst must switch to Tool B to create a ticket, then Tool C to notify the team, then Tool D to investigate. This context-switching adds critical minutes during active incidents.
4. **Inaccessible ML**: Machine learning for anomaly detection exists in academic papers and enterprise products with six-figure price tags. Small-to-mid teams are excluded.
5. **Mobile Blind Spots**: Most SIEM/SOC platforms are desktop-only. When an incident occurs at 2 AM, the on-call engineer opens their phone to a UI that was never designed for touch.

### What AEGIS-LEGION Solves

AEGIS-LEGION eliminates every gap listed above by providing a **single pane of glass** where:

- Events flow in → Rules fire → Incidents are created → Team communicates → Incidents are resolved.
- All of this happens in **one tab**, in **real-time**, on **any device**.

---

## 3. What Makes AEGIS-LEGION Unique

### 🏗️ One-Person Build

**AEGIS-LEGION was designed, architected, and built entirely by a single developer.** Every layer of the stack — from the PostgreSQL schema to the Isolation Forest ML pipeline to the CSS micro-animations — was crafted by one engineer. This is not a template or a fork. It is an original, ground-up implementation.

### 🧠 Integrated ML That Learns Your Infrastructure

Unlike platforms that rely solely on static rules, AEGIS-LEGION includes a **self-training machine learning engine** that learns what "normal" looks like for each individual server. After observing 100 heartbeat cycles (~17 minutes), the Isolation Forest model begins flagging deviations automatically — no configuration required.

### 📱 Mobile-First Design (Not Mobile-Afterthought)

The platform features a dedicated mobile experience, not just a responsive resize:

- **Card-based data views** replace tables on small screens
- **Full-screen chat interface** for incident investigation (iMessage-like UX)
- **Accordion navigation** on the Settings page
- **Touch-optimized buttons** and thumb-friendly interaction zones
- The "Send Test Event" button is hidden on mobile to prevent accidental triggers

### 🔐 Multi-Tenant from Day One

Organizations are isolated at the data layer. Rules, incidents, servers, ML models, and users are all scoped to the tenant. There is no shared state between organizations.

### ⚡ Real-Time Everything

Every action is broadcast instantly via Server-Sent Events (SSE):

- New incidents appear on the dashboard without refreshing
- Chat messages appear in real-time for all participants
- Status changes and assignments are pushed to all connected clients

---

## 4. Timeline

| Phase | Duration | Milestone |
|-------|----------|-----------|
| Architecture & Design | Week 1 | Database schema, API contracts, component hierarchy |
| Backend Core (Auth, Ingest, Rules) | Weeks 2-3 | JWT auth, event pipeline, rule engine, incident CRUD |
| Frontend Dashboard | Weeks 3-4 | React SPA, real-time table, SSE integration |
| ML Pipeline | Week 5 | Isolation Forest training, inference, multi-tenant isolation |
| Incident Response Workflow | Week 6 | Chat/notes, @mentions, notifications, RBAC assignment |
| Notifications (Email/Slack) | Week 7 | Resend API, SMTP fallback, Slack webhooks |
| Mobile UI Overhaul | Week 8 | Card layouts, full-screen chat, accordion settings |
| Security Hardening & Documentation | Week 8+ | Rate limiting, data poisoning protection, production deployment |

**Total Development Time: ~8 weeks (solo developer)**

---

## 5. Complete Feature Reference

### 5.1 User Authentication & Account Management

#### Registration & Login
- Users register with username, email, and password
- First user in a new organization is automatically assigned the **Admin** role
- Login returns a JWT token (30-minute expiry) used for all subsequent API calls
- Passwords are hashed with sha256_crypt (72-byte limit enforced)

#### Password Reset
- Users can request a password reset via email
- A time-limited reset link is sent to the registered email address
- Admins can force-reset any user's password from the Settings page

#### Profile Management
- Users can update their username and full name
- Profile information is displayed in a dedicated Profile Modal accessible from the navigation bar

#### Role-Based Access Control (RBAC)
Three distinct roles govern what users can see and do:

| Capability | Admin | Analyst | Viewer |
|-----------|-------|---------|--------|
| View all org incidents | ✅ | Only assigned servers | ✅ (read-only) |
| Change incident status | ✅ | ✅ | ❌ |
| Assign incidents to others | ✅ | ❌ | ❌ |
| Self-assign ("Take") incidents | ✅ | ✅ (unassigned only) | ❌ |
| Post investigation notes | ✅ | ✅ | ❌ |
| Create/delete rules | ✅ | ✅ | ❌ |
| Manage users | ✅ | ❌ | ❌ |
| Manage server access | ✅ | ❌ | ❌ |
| Generate API keys | ✅ | ✅ | ✅ |
| Rename organization | ✅ | ❌ | ❌ |

---

### 5.2 Server Agent & Telemetry Collection

#### The Agent
A lightweight Python daemon (`agent.py`) is deployed on every server you want to monitor. It requires only `psutil` and `requests` as dependencies.

#### Heartbeat Thread (Every 10 Seconds)
Collects and transmits:
- **CPU usage** (percentage, non-blocking)
- **RAM usage** (percentage)
- **Disk I/O** (read/write in MB/s, calculated as delta between intervals)
- **Network I/O** (inbound/outbound in MB/s, calculated as delta)
- **Process count** (total running PIDs)
- **Active network connections** (TCP/UDP count)
- **Top CPU process** (name and CPU percentage of the highest-consuming process)
- **Operating system** (e.g., "Windows 10", "Linux 5.15.0")
- **IP address** (auto-detected)

#### Monitor Thread (Every 1 Second)
Simulates real-world threat scenarios for testing:
- **10% chance** per second: Simulated failed login attempt
- **1% chance** per second: Simulated malware detection event

#### Authentication
The agent authenticates using an **X-API-Key** header. Keys are generated per-user via the Settings → API Access page.

#### Auto-Discovery
When the backend receives a heartbeat from an unknown hostname, it **automatically registers** the server in the Asset Inventory. No manual setup required.

---

### 5.3 Event Ingestion Pipeline

Every event sent by an agent flows through a multi-stage processing pipeline:

#### Stage 1: Authentication
The ingest endpoint accepts both API Key (`X-API-Key` header) and JWT Bearer tokens. This dual-auth system allows both agents and the dashboard UI to submit events.

#### Stage 2: Rate Limiting
Events are rate-limited to **5 per second per client** using SlowAPI, preventing denial-of-service attacks against the ingestion endpoint.

#### Stage 3: Server Tracking
If the event type is `system_heartbeat`, the backend either:
- **Creates** a new server entry in the Asset Inventory, or
- **Updates** the existing server's last heartbeat timestamp, IP, and OS info

#### Stage 4: ML Anomaly Detection
For heartbeat events, the telemetry data is passed to the Isolation Forest anomaly detector. If an anomaly is detected, a synthetic `ml_anomaly` event is generated and fed back into the rule engine.

#### Stage 5: Rule Engine Processing
The event is evaluated against all active rules for the organization. Matched rules trigger incident creation or merging.

#### Stage 6: Real-Time Broadcast
The processed event and any resulting incidents are broadcast to all connected dashboard clients via SSE.

---

### 5.4 Rule Engine

#### Overview
The rule engine is the core detection mechanism. Users define rules with conditions that match against incoming event payloads. When a match occurs, an incident is automatically created.

#### Rule Configuration
Each rule consists of:
- **Name**: Human-readable identifier (e.g., "High CPU Alert")
- **Description**: Explanation of what the rule detects
- **Severity**: The severity assigned to incidents created by this rule (low/medium/high/critical)
- **Target Server**: Optional server-specific targeting. If set, the rule only fires for events from that specific hostname. If unset, the rule applies globally.
- **Conditions**: A list of field/operator/value triples using dot notation

#### Supported Operators
| Operator | Type | Example |
|----------|------|---------|
| `equals` | Exact string match | `event_type` equals `login_failed` |
| `contains` | Substring match | `data.path` contains `.exe` |
| `gt` | Greater than (numeric) | `data.cpu` gt `90` |
| `lt` | Less than (numeric) | `data.ram` lt `5` |

#### Available Fields (Dot Notation)
- **Top-Level**: `event_type`, `source`, `severity`
- **Universal Data**: `data.ip`, `data.os`
- **Hardware Metrics**: `data.cpu`, `data.ram`, `data.disk_read_mb`, `data.disk_write_mb`, `data.net_in_mb`, `data.net_out_mb`, `data.net_connections`, `data.top_process`
- **Threat-Specific**: `data.fail_count`, `data.user` (login events), `data.path`, `data.hash` (malware events)

#### Incident Deduplication (Smart Merge)
When a rule matches, the engine first checks if an **open incident** already exists for the same source, event type, and user. If one exists:
- The alert count is incremented
- The description is appended with the new event details
- The severity is **upgraded** if the new rule's severity is higher than the existing incident's
- No duplicate incident is created

#### Priority Override System
Targeted rules (server-specific) are always evaluated **before** global rules. If a targeted rule matches with severity "critical" and a global rule matches with "medium", the incident will carry the "critical" severity.

#### Fallback Rules
If no user-defined rules exist, hardcoded fallback rules handle:
- **Brute-force logins**: 3+ failed login attempts → High severity incident
- **Critical threat types**: `malware_detected`, `ransomware_activity`, `privilege_escalation` → High severity
- **ML anomalies**: Anomaly detection triggers → Medium severity
- **Manual tests**: Dashboard "Send Test Event" button → Low severity

---

### 5.5 ML-Powered Anomaly Detection

#### Algorithm
Uses **scikit-learn's Isolation Forest** — an unsupervised learning algorithm that isolates anomalies by randomly partitioning the feature space. It excels at detecting outliers in high-dimensional data without requiring labeled training examples.

#### Why Isolation Forest?
1. **No labeled data required**: The model learns "normal" from observation, making it ideal for environments where you don't know what attacks look like yet.
2. **Low sample requirement**: Only 100 samples needed to train (vs. thousands for neural networks).
3. **Fast inference**: Predictions are near-instant, allowing real-time scoring on every heartbeat.
4. **Per-server models**: Each server gets its own model, so a database server's "normal" (high disk I/O) won't trigger alerts when compared to a web server's baseline.

#### Feature Vector
The model trains on 5 dimensions of system telemetry:
1. CPU Usage (%)
2. RAM Usage (%)
3. Disk Write Rate (MB/s)
4. Network Outbound (MB/s)
5. Process Count

#### Training Lifecycle
1. **Buffering** (0-100 events): Heartbeats are collected but no predictions are made. A progress bar on the ML Monitor shows collection status.
2. **Training**: At 100 events, the Isolation Forest model is fit and saved to disk as a `.pkl` file.
3. **Pending Approval**: The model enters a dormant state. This prevents **data poisoning** — an attacker who compromises a server during the training window cannot inject malicious baselines.
4. **Admin Approval**: An admin reviews the model status on the ML Monitor page and explicitly approves it.
5. **Active Inference**: The model scores every incoming heartbeat. Events scoring below the anomaly threshold generate an `ml_anomaly` incident.
6. **Reset**: If infrastructure changes significantly (e.g., server upgrade, new workloads), the admin can reset the model to restart training.

#### Multi-Tenant Model Isolation
Models are stored per `(organization_id, server_hostname)` combination. Organization A's models never interact with Organization B's data.

---

### 5.6 Incident Management

#### Incident Properties
- **Organization-Scoped ID**: Friendly incrementing IDs (1, 2, 3...) per organization, independent of the global database primary key
- **Title**: Auto-generated from the rule name or event type
- **Description**: Contains the triggering event data and merge history
- **Severity**: Low / Medium / High / Critical (color-coded badges)
- **Status**: Open → Investigating → Mitigated → Resolved → Closed
- **Alert Count**: Number of events merged into this incident
- **Source**: The server hostname that generated the event
- **Assignees**: Many-to-many relationship — multiple users can be assigned

#### Status Workflow
Status changes are:
- Logged as **system notes** in the incident chat
- **Broadcast in real-time** to all connected dashboard users
- Visually color-coded (blue=open, purple=investigating, cyan=mitigated, green=resolved)

#### Assignment System
- **Analyst "Take"**: Analysts can self-assign unassigned incidents with a single tap
- **Admin Multi-Assign**: Admins see a popover with all eligible users (filtered by server access) and can assign multiple team members
- **Assignment Candidates**: The system intelligently filters candidates based on server access permissions. If no server-specific access is configured, all organization users are shown.
- Assignments generate **in-app notifications** for the assigned users

---

### 5.7 Incident Messaging / Investigation Chat

This is the **most frequently used feature** and has been optimized for premium usability.

#### Chat Architecture
Every incident has a threaded conversation log consisting of two types of messages:
1. **User Notes**: Investigation findings, questions, and updates posted by analysts and admins
2. **System Logs**: Automated entries for status changes, assignments, and other system events (displayed with distinct "SYSTEM:" prefix and muted styling)

#### @Mention System
- Type `@` to trigger an autocomplete dropdown showing all organization users
- **@username**: Sends an in-app notification to that specific user
- **@everyone**: Sends notifications to all admins plus all users with access to the incident's source server
- Mentions are parsed server-side using regex, preventing client-side spoofing

#### Notification Generation
When a user is @mentioned:
- A `Notification` record is created in the database
- The notification includes a deep link to the specific incident (`/dashboard?incidentId=X`)
- The notification bell in the navbar updates with unread count

#### Mobile Chat Experience
On mobile devices (≤768px viewport), the incident modal transforms into a **full-screen native-feeling chat interface**:
- Takes over 100% of viewport width and height (using `100dvh` for iOS Safari compatibility)
- **Sticky frosted-glass input bar** at the bottom with `backdrop-filter: blur(12px)`
- Large **"← Back" button** replacing the small desktop "✕" for thumb-friendly navigation
- Messages render as full-width bubbles optimized for touch
- System messages are visually distinct with muted styling and smaller font

#### Desktop Chat Experience
On desktop, the chat appears as a sleek modal overlay with:
- 80vh height with internal scroll
- Real-time message updates via SSE
- Autocomplete suggestions for @mentions
- Keyboard-friendly input (Enter to send)

---

### 5.8 Server Asset Inventory

#### Auto-Discovery
Servers are automatically registered when their agent sends the first heartbeat. No manual configuration is needed.

#### Server Properties
- **Name**: Editable display name (defaults to hostname)
- **Hostname**: System hostname reported by the agent
- **IP Address**: Auto-detected from heartbeat data
- **OS Info**: Operating system and version
- **Status**: Online (heartbeat within threshold) / Offline
- **Last Heartbeat**: Timestamp of last received heartbeat

#### Server Access Control (Admin Feature)
Admins can configure which analysts have access to which servers:
- **Server Access Modal**: Shows all organization users and allows toggling access per server
- **Impact on Incident Visibility**: Analysts only see incidents from servers they have been granted access to
- **Impact on Assignment Candidates**: Only users with server access appear in the assignment popover

#### Server Actions
- **Rename**: Any user can rename a server for better identification
- **Delete**: Admins can permanently remove a server from the inventory
- **Access Management**: Admins can grant/revoke server access for individual users

---

### 5.9 Settings & Administration

The Settings page is organized into five sections. On mobile, these sections are displayed as **collapsible accordions** with animated SVG chevrons. On desktop, they appear as standard stacked panels.

#### User Profile
Displays the current user's username, role, email, and organization. Admins can rename the organization (affects all users).

#### User Management (Admin Only)
- **Create User**: Form to create new accounts with username, email, password, and role selection
- **Existing Users Table**: Lists all organization users with their role, email, and org
- **Reset Password**: Admins can force-reset any user's password
- **Delete User**: Admins can remove users from the organization

#### API Access
- **API Key Display**: Shows the current API key (masked) with a copy button
- **Generate/Regenerate**: Creates a new API key (old key is invalidated)
- **Key Countdown**: New keys are displayed in full for 10 seconds with a countdown timer before being masked
- **Download Agent**: One-click download of the `agent.py` script
- **Audit Trail**: Key generation is logged and an email confirmation is sent

#### Audit History
A chronological log of all security-relevant actions:
- User logins, registrations, and password changes
- API key generations
- Server deletions
- All entries include timestamp, actor username, action type, and details

#### Asset Inventory (Servers)
Lists all registered servers with:
- Online/offline status indicator
- Server details (name, hostname, IP, OS, last seen)
- Action buttons: Rename, Access Control, Delete

---

### 5.10 Dashboard & Visualization

#### Quick Stats Panel
Four stat cards showing real-time counts:
- Total Incidents
- Open Incidents
- Critical Incidents
- Active Servers

#### Incident Table (Desktop)
A sortable data table with columns for:
- ID (organization-scoped), Title, Server, Assignee avatars, Alert Count, Severity badge, Status dropdown, View button, Timestamp
- Sortable by Alert Count, Severity, and Timestamp

#### Incident Cards (Mobile)
On mobile, the table is replaced by **stacked cards** showing:
- Severity badge + ID in the header
- Title as the card heading
- Status dropdown and server info in a 2-column grid
- Full-width "VIEW" button + role-appropriate action buttons ("⚡ TAKE" for analysts, "+ ASSIGN" for admins)

#### Threat Trend Chart
A time-series line chart (Chart.js) showing incident volume over time, allowing teams to spot escalation patterns.

#### Activity Feed
A real-time scrolling feed of the latest events, notes, and status changes — powered by SSE.

#### ML Monitor
A dedicated panel showing:
- Per-server ML model status (Training / Pending Approval / Active)
- Training progress bar (X/100 samples)
- Approve and Reset buttons (Admin only)

---

### 5.11 Navigation & Mobile Experience

#### Desktop Navigation
A full horizontal navigation bar with:
- AEGIS-LEGION logo/brand
- Page links: Dashboard, Rules, Settings
- Notification bell with unread count badge
- User profile button with dropdown
- Logout button

#### Mobile Navigation
On screens ≤768px:
- The desktop menu is hidden
- A **hamburger menu button** (☰) appears
- Tapping it reveals a **full-width dropdown** with all navigation links stacked vertically
- The dropdown has a dark glassmorphism background with `backdrop-filter: blur(20px)`

#### Landing Page
A public-facing landing page at the root URL (`/`) showcasing:
- Platform overview and value proposition
- Feature highlights
- Call-to-action buttons for Login and Registration
- Animated dotted surface background effect

---

### 5.12 Notification System

#### In-App Notifications
- Generated by @mentions in incident chat
- Generated by incident assignments
- Displayed via a **bell icon** in the navbar with an unread count badge
- Each notification includes a title, message preview, and a deep link to the relevant incident

#### Email Notifications
Sent via Resend API (primary) or SMTP (fallback) for:
- **Welcome emails**: Branded HTML email with Jinja2 templating and embedded dashboard preview image
- **API key confirmations**: Sent to the key generator
- **Admin alerts**: New user registrations, API key generations by team members
- **Critical threat alerts**: Immediate email when high/critical severity incidents are created
- **Password reset links**: Time-limited reset URLs

#### Slack Notifications
Optional Slack channel integration via incoming webhooks for team-wide alerting.

---

### 5.13 Real-Time Updates (SSE)

The platform uses **Server-Sent Events** for live data synchronization:

- **Why SSE over WebSockets?** SSE is simpler, works through HTTP proxies and load balancers, auto-reconnects on connection loss, and is sufficient for server-to-client push (which is the only direction needed for a monitoring dashboard).
- **Architecture**: A global `Broadcaster` singleton maintains an `asyncio.Queue` per connected client. Events are pushed non-blocking; slow consumers don't block the publisher.
- **What's broadcast**: New events, incident creation/merge, status changes, chat messages, assignment updates.
- **Frontend**: Uses the `EventSource` browser API with automatic reconnection.

---

### 5.14 Security Features

| Feature | Implementation |
|---------|---------------|
| **JWT Authentication** | HS256-signed tokens, 30-minute expiry, mandatory `JWT_SECRET` |
| **Password Security** | sha256_crypt hashing, 72-byte max length enforcement |
| **Rate Limiting** | SlowAPI middleware, 5 req/sec on ingest endpoint |
| **ML Anti-Poisoning** | Trained models require admin approval before active inference |
| **RBAC** | Three-tier role system enforced at every API endpoint |
| **Multi-Tenant Isolation** | All queries filtered by `organization_id` |
| **Audit Logging** | All security-relevant actions logged with actor, action, and timestamp |
| **API Key Rotation** | Keys can be regenerated at any time, invalidating the old key |
| **Sensitive File Protection** | `.gitignore` excludes `*.db`, `*.sqlite`, and credential files |

---

## 6. Platform Screenshots & UI Highlights

### Desktop Dashboard
- Dark cyberpunk aesthetic with custom CSS variables (`--accent`, `--panel-border`, `--font-mono`)
- Glassmorphism cards with `backdrop-filter` effects
- Smooth `animate-fade-in` transitions on page load
- Color-coded severity badges (green=low, yellow=medium, orange=high, red=critical)
- Color-coded status indicators (blue=open, purple=investigating, cyan=mitigated, green=resolved)

### Mobile Experience
- **Card-based incident list** replacing horizontal-scroll tables
- **Full-screen incident chat** with sticky frosted input bar
- **Accordion settings** with animated SVG chevron indicators
- **Hidden test buttons** preventing accidental triggers
- **Touch-optimized buttons** with full-width tap targets

---

## 7. Deployment & Hosting

The platform is currently deployed as:

| Component | Host | URL |
|-----------|------|-----|
| Frontend | Vercel | `aegis-legion.vercel.app` |
| Backend | Render | `aegis-legion.onrender.com` |
| Database | PostgreSQL (Render) | Internal connection |

The agent can be deployed on **any Linux or Windows server** as a background service.

---

## 8. Future Roadmap

- **Webhook Integrations**: PagerDuty, Jira, Microsoft Teams
- **Dashboard Customization**: Drag-and-drop widget layouts
- **Advanced ML**: Multi-model ensemble (Isolation Forest + Autoencoder)
- **Compliance Reporting**: SOC 2 and ISO 27001 report generation
- **Agent Auto-Update**: Remote agent version management from the dashboard

---

*AEGIS-LEGION — Built from scratch, by one engineer, for the future of cloud security.*
