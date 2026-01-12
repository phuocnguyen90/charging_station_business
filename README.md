# Solar ROI Platform

A comprehensive web application for estimating Solar Energy potential, Return on Investment (ROI), and connecting Clients with Installers.

## Features

- **Advanced Simulation**: Physics-based modeling of Solar generation, Battery usage, and Grid interaction.
- **Globalized**: Multi-currency and Multi-language (English/Vietnamese) support.
- **Marketplace**: Installers can manage specific inventory with regional pricing.
- **Smart Wizard**: Simple client onboarding with automated usage profiling.

## Tech Stack

- **Frontend**: Next.js, Tailwind CSS, Shadcn UI.
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL.
- **Infrastructure**: Docker ready (planned).

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+

### Running Locally

1. **Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python3 -m uvicorn main:app --reload --port 8000
   ```

2. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Access at `http://localhost:3001` (if 3000 is taken).

## Running via Docker

To spin up the entire stack with a single command (ensure you stop any local instances first):

```bash
docker-compose up --build
```

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:5001
- **API Docs**: http://localhost:5001/api/v1/docs

## Documentation
See `AGENTS.md` for architectural details and agent handover context.
