# AGENTS.md - Solar Business Project Context

## 1. Project Overview
**Goal**: Build a multi-tenant Solar ROI & Estimation platform.
**Target Users**: 
- **Clients**: Homeowners/Business owners looking for solar estimates (Anonymous Wizard -> Account & Save).
- **Installers**: Companies managing inventory, creating branded quotes, and receiving leads.
- **Admins**: System oversight, catalog management.

## 2. Architecture
**Stack**:
- **Frontend**: Next.js 15+ (App Router), TypeScript, Tailwind CSS, Shadcn UI.
- **Backend**: FastAPI (Python 3.10+), SQLAlchemy (Async/Sync mixed currently using Sync for simplicity), Pydantic.
- **Database**: PostgreSQL (Production), SQLite (Dev).
- **Auth**: JWT (OAuth2PasswordBearer).

**Key Directories**:
- `backend/`: FastAPI application.
  - `core/`: Config, Security, Localization.
  - `models/`: SQLAlchemy tables (`user`, `inventory`, `branding`, `quote`, `analytics`).
  - `routers/`: API endpoints (`v1`).
  - `services/`: Business logic (`calculator.py` for physics simulation).
  - `schemas/`: Pydantic DTOs.
- `frontend/`: Next.js application.
  - `src/app/[locale]/`: i18n routed pages.
  - `src/components/ui/`: Shadcn components.
  - `src/lib/api.ts`: Axios client.
  - `messages/`: JSON translation files (`en.json`, `vi.json`).

## 3. Core Features & Status

### A. Simulation Engine (DONE)
- **Logic**: Physics-based calculation (Solar Irradiance, Battery State of Charge, Grid Rates).
- **Location**: `backend/services/calculator.py`.
- **Status**: Ported from POC, exposed via `/api/v1/simulation/run`.

### B. User Management (DONE)
- **Roles**: Client, Installer, Admin.
- **Auth**: JWT Login/Register implemented.
- **Status**: Endpoints ready, Frontend Auth UI pending.

### C. Inventory System (Schema First) (DONE)
- **Models**: 
  - `Brand` -> `ProductModel` (Global Catalog).
  - `InventoryListing` (Installer specific pricing/stock).
- **Polymorphism**: Strict typing for `SolarPanelSpecs`, `BatterySpecs`, `InverterSpecs`.

### D. Client Wizard (PARTIAL)
- **Frontend**: Implemented at `/dashboard/client/wizard`.
- **Flow**: Anonymous access -> Input Bill/Location -> View Estimate.
- **Pending**: "Save Quote" functionality (requires Login).

### E. Analytics (DONE)
- **Models**: `UserActivityLog`, `SimulationLog`.
- **Goal**: Feed future Recommender System.

## 4. "Schema First" Principles
We prioritize defining robust data structures before UI.
- **QuoteRequest**: Flexible inputs (`monthly_bill`, `usage_profile`) + Context (`raw_transcript` for LLM).
- **Quote**: Concrete configuration linked to specific `InventoryListing` items.

## 5. Development Instructions

### Backend
```bash
cd backend
# Install dependencies (including email-validator, uvicorn, etc.)
pip install -r requirements.txt
# Run Server (Port 8000)
python3 -m uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
# Install dependencies
npm install
# Run Server (Port 3001)
npm run dev
```

## 6. Next Steps for Agent
1.  **Authentication UI**: Build `/auth/login` and `/auth/register` pages in Frontend.
2.  **Save Quote**: Connect the Wizard "Save" button to the Auth flow and then POST to `/api/v1/quotes`.
3.  **Installer Dashboard**: CRUD for `InventoryListing`.
