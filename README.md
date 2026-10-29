# GitLite: Containerized Distributed Object Storage & Version Control Backend

[![FastAPI](https://img.shields.io/badge/framework-FastAPI-teal.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/container-Docker%20Compose-2496ED.svg)](https://www.docker.com/)
[![Alembic](https://img.shields.io/badge/migration-Alembic-red.svg)](https://alembic.sqlalchemy.org/)

A production-engineered, containerized version-control backend and isolated object-storage engine built with FastAPI, PostgreSQL, and Docker. Implements multi-stage database lifecycle management, cryptographic authentication, and path-sanitized workspace file operations.

---

## Architecture & Systems Overview

GitLite separates stateless REST request handling, database connection pooling, and filesystem-backed workspace isolation into decoupled container boundaries:

```mermaid
flowchart TD
    Client["Client / Web UI (HTML5, JS Fetch, CSS)"]

    subgraph DockerBoundary["Docker Compose Isolated Network"]
        subgraph Gateway["FastAPI Application Gateway"]
            CORS["CORS Middleware (Configurable Origins)"]
            AuthGuard["Security & Auth Guard (OAuth2 Bearer, bcrypt, JWT)"]
            APIRouter["Resource Routers (Users, Repositories, Files)"]
        end

        subgraph StorageLayer["Data & Object Storage Tier"]
            ORM["SQLAlchemy ORM (Connection Pool / SessionLocal)"]
            DB[(PostgreSQL Relational DB)]
            InitProbe["Readiness Probe (wait_for_db.py)"]
            Migrate["Alembic Migration Engine (alembic upgrade head)"]
            DiskStorage["Isolated Workspace File Store (storage/)"]
        end
    end

    Client <-->|HTTP / REST (JWT Bearer)| CORS
    CORS --> AuthGuard
    AuthGuard --> APIRouter
    APIRouter -->|Structured Metadata| ORM
    APIRouter -->|Sanitized Multipart File Streams| DiskStorage
    ORM <--> DB
    InitProbe -->|TCP Socket Probe :5432| DB
    InitProbe -->|On Healthy Connection| Migrate
    Migrate -->|Apply Schema Head| DB
```

---

## Technical Specifications & Request Lifecycle

### 1. Ingress, CORS & Security Pipeline
- **Configurable Ingress**: Configurable via `ALLOW_ORIGINS` environment variables with strict origin matching.
- **Cryptographic Security**: Password hashing powered by Passlib (`bcrypt`), stateless JWT token issuance, and dependency injection guards via `FastAPI.Depends(get_current_user)`.
- **Admin Seeding**: Automated initialization of baseline administrative users (`ADMIN_EMAIL`, `ADMIN_PASSWORD`) upon deployment bootstrap.

### 2. Database Resilience & Schema Migration
- **TCP Readiness Probe (`wait_for_db.py`)**: Interrogates the PostgreSQL socket directly on startup, blocking backend initialization until the database is fully ready to accept connections.
- **Alembic Versioning**: Automatic schema migrations apply declarative SQLAlchemy model updates deterministically across environments.
- **Session Pooling**: Managed `SessionLocal` scope per request with automatic transaction rollback upon unhandled exceptions.

### 3. File System & Workspace Storage Engine
- **Path Sanitization**: Resolves file paths defensively within designated user workspaces to prevent directory traversal attacks (`../`).
- **Multipart Upload Streams**: Handles high-throughput file uploads via `UploadFile` with chunked streaming to local persistent disk volumes.

---

## Directory Organization

```text
GitLite/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application entry, CORS, and endpoint definitions
│   │   ├── auth.py          # JWT generation, token verification, and OAuth2 routes
│   │   ├── security.py      # Password hashing algorithms (bcrypt)
│   │   ├── models.py        # SQLAlchemy relational database tables
│   │   ├── schemas.py       # Pydantic serialization and validation schemas
│   │   ├── crud.py          # Database queries and transaction operations
│   │   ├── database.py      # Engine connection pooling and session makers
│   │   └── storage/         # Local workspace and file system storage repository
│   ├── alembic/             # Database migration version files
│   ├── alembic.ini          # Alembic environment and connection config
│   ├── Dockerfile           # Optimized container build specification
│   ├── docker-compose.yml   # Multi-service networking and volume declarations
│   ├── requirements.txt     # Python dependencies
│   └── wait_for_db.py       # TCP connection readiness probe for PostgreSQL
├── css/                     # Client stylesheets
├── js/                      # Frontend client logic & REST API consumers
├── index.html               # File browser & repository management portal
├── login.html               # Authentication interface
└── signup.html              # Registration interface
```

---

## Deployment & Quickstart

```bash
# 1. Navigate to backend directory
cd backend

# 2. Start services with Docker Compose
docker-compose up --build -d

# 3. Stream startup logs & migration execution
docker-compose logs -f backend

# 4. Access OpenAPI interactive documentation
# Open: http://localhost:8000/docs
```

---

## Author
**Hemal Shah**  
Systems & AI Platform Engineer  
[https://tensix.in](https://tensix.in) | [github.com/hemal9102](https://github.com/hemal9102)
