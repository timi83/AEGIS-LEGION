# Cloud-Threat-Detection-Platform (Local Scaffold)

This is a minimal, local scaffold of the **CTDIRP** project to get you started quickly.

## What's included
- FastAPI backend with a simple `/ingest` endpoint
- Tiny placeholder detection engine (rule + simple heuristic)
- Dockerfile for the backend
- docker-compose with a Postgres service (for future use)

## Quick start (Linux / macOS / Windows WSL / Windows with Docker)

1. Install Docker and Docker Compose.
2. Open a terminal in the project root (where `docker-compose.yml` is).
3. Build and run everything:

   ```bash
   docker-compose up --build
   ```

4. The API will be available at `http://localhost:8000`.

5. Test the ingest endpoint (example):

   ```bash
   curl -X POST http://localhost:8000/ingest -H "Content-Type: application/json" -d '{"value": 2500, "user": "alice"}'
   ```

   Example response:

   ```json
   {"alert": {"score": 0.918, "anomaly": true, "reasons": ["high_value"]}}
   ```

## Next steps (suggested)
- Replace the placeholder detector with an Autoencoder or IsolationForest trained on realistic logs.
- Add persistence (Postgres) for events and alerts.
- Add authentication and API schemas with Pydantic models.
- Add integration tests and GitHub Actions for CI.

## Troubleshooting
- If the backend fails to install packages during Docker build, try increasing Docker build resources or build locally in a virtualenv.

## Notes
This scaffold is intentionally minimal to help you focus on the core detection logic before expanding into infra, CI/CD, and cloud deployment.
