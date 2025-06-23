# Moonrider Identity Reconciliation Microservice

## Overview
This service consolidates user identities across different emails and phone numbers, as required by the Moonrider assignment. It exposes a `/identify` endpoint that links contacts and returns unified contact info.

## Features
- Reconciles identities using email/phone, supporting primary/secondary contact logic
- Returns all related emails, phone numbers, and secondary contact IDs
- Fully containerized (Docker)
- Ready for CI/CD and Kubernetes deployment

## Getting Started

### Local Development
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Run Tests
```bash
pytest
```

### Using Docker
```bash
docker build -t identity-recon .
docker run -p 8000:8000 identity-recon
```

### API Usage
POST `/identify`
```json
{
  "email": "user@example.com",
  "phoneNumber": "1234567890"
}
```
Response:
```json
{
  "primaryContactId": 1,
  "emails": ["user@example.com"],
  "phoneNumbers": ["1234567890"],
  "secondaryContactIds": []
}
```

## Kubernetes Deployment
- See `k8s/` directory for manifests.

## CI/CD
- GitHub Actions workflow in `.github/workflows/ci.yml` builds, tests, and pushes Docker images.

---
For system design and architecture, see `SYSTEM_DESIGN.md`.
