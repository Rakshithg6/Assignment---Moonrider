# System Design: Identity Reconciliation Microservice

## Architecture
- **FastAPI** backend with `/identify` endpoint
- **SQLite** for local development, swappable to PostgreSQL/MySQL
- **SQLAlchemy ORM** for DB access
- **Docker** for containerization
- **Kubernetes** manifests for scalable deployment
- **CI/CD** via GitHub Actions

## Core Logic
- Contacts are linked by email or phone, with one primary per group (oldest contact)
- New info creates secondary contacts, always linked to the primary
- Merging ensures only one primary per group, others are secondary
- All related emails/phones are deduped in response

## Database Schema
- See `app/models.py` for details

## Error Handling
- Returns 400 if both email and phone are missing
- Handles edge cases: overlapping contacts, repeated requests, etc.

## Deployment Flow
1. Build Docker image
2. Push to registry
3. Deploy to Kubernetes with manifests in `k8s/`
4. HPA and Ingress for scalability and routing

## Security & Observability
- Can be extended with TLS, RBAC, and monitoring (Prometheus, Grafana)
- Logging can be added for audit trails
