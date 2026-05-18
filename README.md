# TEX v2

AI-powered basketball scouting platform. Coaches upload game film; TEX returns structured PDF scouting reports.

## Status

Early development. See `ROADMAP.md` for current phase and next milestones.

## Run locally

**Prerequisites:** Docker + Docker Compose, Node.js 22+, Python 3.12, a Google Cloud project with Gemini API access.

### Backend

```bash
cp backend/.env.example backend/.env
# Fill in: NEON_*, GEMINI_API_KEY, CLOUDFLARE_R2_*, CLERK_*, STRIPE_*, SENTRY_DSN
pip install -r backend/requirements.txt   # required for mypy + pre-commit to match CI
docker compose up
```

API runs on `http://localhost:8001`. Worker + Redis come up with the compose stack; the Postgres database is hosted on Neon (cloud), connected via `NEON_*` env vars.

### Frontend

```bash
cp frontend/.env.example frontend/.env.local
# Fill in: NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY, CLERK_SECRET_KEY, NEXT_PUBLIC_API_BASE_URL
cd frontend && npm install && npm run dev
```

Frontend runs on `http://localhost:3000`.

### Pre-commit hooks (recommended before pushing)

```bash
pip install pre-commit && pre-commit install
```

First run is slow (~30–60s) because mypy installs `backend/requirements.txt` into a hook-local env. Subsequent runs are cached. See `DECISIONS.md` D-021 for the rationale.

## Documentation

Start with `CLAUDE.md` for product context and working style, then `ARCHITECTURE.md` for system design, then `ROADMAP.md` for current state.

| Doc | Purpose |
|---|---|
| `CLAUDE.md` | Working style, conventions, must-read first |
| `ARCHITECTURE.md` | System design and component map |
| `ROADMAP.md` | Phase-by-phase progress, current milestone |
| `STACK.md` | Technology choices and rationale |
| `DECISIONS.md` | Numbered architectural decisions (D-001 onward) |
| `PROMPTS.md` | Gemini prompt versioning |
| `SCHEMA.md` | Postgres schema reference |
| `FLOWS.md` | End-to-end request flows |
| `EVALS.md` | Eval gates per phase |
| `COSTS.md` | Cost model per report |
| `PRD.md` | Product requirements |
| `VISION.md` | Long-term direction |
| `AGENTS.md` | RLHF training mode notes |
| `MCP.md` | MCP server integrations |
| `AI_STRATEGY.md` | AI/ML strategy |

## License

Proprietary. All rights reserved.
