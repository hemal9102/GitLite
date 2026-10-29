# GitLite

[![FastAPI](https://img.shields.io/badge/framework-FastAPI-teal.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/container-Docker%20Compose-2496ED.svg)](https://www.docker.com/)
[![Alembic](https://img.shields.io/badge/migration-Alembic-red.svg)](https://alembic.sqlalchemy.org/)

A containerized distributed version-control backend and object management platform built with FastAPI, PostgreSQL, and Docker. Features automated database migrations, JWT authentication, and isolated repository workspace orchestration.

---

## Architecture Overview

GitLite provides a modular microservice architecture decoupling API routing, database schema versioning, and file-tree storage:

`
                            +-----------------------------+
                            |         Client / UI         |
                            +--------------+--------------+
                                           | HTTP / REST
                                           v
                            +-----------------------------+
                            |       FastAPI Gateway       |
                            |                             |
                            |  * OAuth2 / JWT Auth Guard  |
                            |  * Repo & File Management   |
                            |  * Async Pydantic Schemas   |
                            +--------------+--------------+
                                           |
                    +----------------------+----------------------+
                    |                                             |
                    v                                             v
     +------------------------------+             +------------------------------+
     |     PostgreSQL Database      |             |   Object / Workspace Store   |
     |                              |             |                              |
     |  * Users & Org Schemas       |             |  * Repository File Trees     |
     |  * Alembic Migration Engine  |             |  * Isolated Commit Hashes    |
     |  * Connection Pooling        |             |  * Structured Metadata Logs  |
     +------------------------------+             +------------------------------+
`

---

## Core Capabilities

- **Asynchronous REST API**: High-concurrency async endpoints powered by FastAPI and SQLAlchemy ORM.
- **Relational Integrity & Schema Versioning**: Automated schema migration lifecycle managed via Alembic (lembic upgrade head), including healthcheck wait-for-db scripts.
- **Secure Authentication Layer**: Role-based access control, cryptographic password hashing (bcrypt), and stateless JWT session tokens.
- **Multi-Container Orchestration**: Fully reproducible Docker Compose setup establishing isolated networks between API gateways, databases, and local storage volumes.

---

## Directory Structure

`	ext
GitLite/
├── backend/
│   ├── app/                 # FastAPI application core (models, schemas, routers, auth)
│   ├── alembic/             # Database migration scripts & version tracking
│   ├── alembic.ini          # Migration configuration
│   ├── Dockerfile           # Optimized multi-stage backend container
│   ├── docker-compose.yml   # Multi-service runtime configuration
│   ├── requirements.txt     # Locked production dependencies
│   └── wait_for_db.py       # TCP connection readiness probe for PostgreSQL
├── css/                     # UI stylesheet assets
├── js/                      # Frontend client logic & API fetch layer
├── index.html               # Main application portal
├── login.html               # Authentication interface
└── signup.html              # Registration portal
`

---

## Quickstart (Docker Compose)

### 1. Launch Services
`ash
cd backend
docker-compose up --build -d
`

### 2. Verify Database Migrations
The wait_for_db.py readiness probe blocks application startup until PostgreSQL reports healthy socket availability, after which Alembic executes migrations automatically:
`ash
docker-compose logs -f backend
`

### 3. API Documentation
Once running, interactive OpenAPI/Swagger documentation is available at:
- http://localhost:8000/docs
- http://localhost:8000/redoc

---

## Author
**Hemal Shah**  
Systems & AI Platform Engineer  
[https://tensix.in](https://tensix.in) | [github.com/hemal9102](https://github.com/hemal9102)
