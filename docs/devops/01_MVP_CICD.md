# Epic 1: MVP CI/CD Pipeline

**Objective**: Establish a robust Continuous Integration and Continuous Deployment (CI/CD) pipeline to automate testing, building, and deploying the Solar ROI MVP.

**Status**: Planning
**Owner**: DevOps Team (AI)

## 1. Containerization (Docker)
We need to containerize both applications to ensure consistent environments across Development, Staging, and Production.

- [ ] **Backend Dockerfile**: 
    - Output: Optimized Python 3.12 slim image.
    - Requirements: `pyproject.toml` or `requirements.txt`.
    - Verification: `docker run` boots FastAPI on port 5001.
- [ ] **Frontend Dockerfile**:
    - Output: NodeJS 20 Alpine image.
    - Stage 1: Build (install deps, build Next.js).
    - Stage 2: Serve (standalone output or `npm start`).
    - Verification: `docker run` boots Next.js on port 3001.
- [ ] **Docker Compose (Local Dev)**:
    - Orchestrate Backend, Frontend, and Database (Postgres/SQLite).
    - Network config to allow container communication.

## 2. Continuous Integration (CI)
Automate quality checks on every commit/PR.

- [ ] **GitHub Actions Workflow (`.github/workflows/ci.yml`)**:
    - **Backend Job**:
        - Install Python.
        - Run `pylint` / `ruff`.
        - Run `pytest` (Unit tests for Simulation).
    - **Frontend Job**:
        - Install Node.
        - Run `npm run lint` (ESLint).
        - Run `npm run type-check` (TypeScript).
        - Run `npm run build` (Verify buildability).

## 3. Testing Strategy
Ensure the critical paths are covered.

- [ ] **Backend Unit Tests**: Cover `SimulationEngine` logic.
- [ ] **API Tests**: Cover `/auth`, `/simulation`, `/quotes` endpoints.
- [ ] **Frontend Smoke Tests**: Verify critical pages load (Login, Wizard).

## 4. Continuous Deployment (CD) - MVP
Simple deployment strategy for the initial release.

- [ ] **Production Environment Setup**:
    - VPS (e.g., Ubuntu) or PaaS.
    - Reverse Proxy (Nginx) setup for routing domains -> ports.
- [ ] **Deployment Script**:
    - `deploy.sh`: Pulls latest code, builds images, restarts containers.
    - Secrets management (Env vars).

## Acceptance Criteria
- [ ] `docker compose up` starts the full stack locally with one command.
- [ ] CI pipeline passes green on the main branch.
- [ ] A documented "Production Deployment Guide" exists.
