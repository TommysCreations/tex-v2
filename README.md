# TEX v2

AI-powered basketball scouting platform. A coach uploads game film; TEX returns a master PDF scouting report.

The product loop and architectural reasoning live in the canonical docs (see [Documentation](#documentation) below). This README is the front door — read [CLAUDE.md](./CLAUDE.md) first for the full picture.

## Local development

### Prerequisites

- Docker (Mac: Docker Desktop; Linux: Docker Engine + Compose plugin)
- Python 3.12 + `pip`
- Node.js 22 + `npm`

### One-time setup

```bash
# Backend env
cp backend/.env.example backend/.env
# ... fill in NEON_*, REDIS_URL, GEMINI_API_KEY, CLERK_SECRET_KEY,
#     CLOUDFLARE_R2_*, STRIPE_SECRET_KEY, etc.

# Frontend deps
cd frontend && npm install && cd ..

# Pre-commit hooks (gitleaks, ruff, mypy, eslint, prettier)
pip install pre-commit
pre-commit install

# IMPORTANT: install backend deps locally too, otherwise mypy (via pre-commit
# AND directly) will run under ignore_missing_imports and silently miss type
# errors that CI catches. See D-021 for the rationale.
pip install -r backend/requirements.txt
```

### Run the stack

```bash
docker compose up -d           # API + worker + Redis
cd frontend && npm run dev     # Next.js dev server on :3000
```

API health: `curl http://localhost:8001/health` → `{"status":"ok"}`.

### Run the linters / type checkers locally

```bash
# Backend
cd backend && python3 -m ruff check . && python3 -m ruff format --check . && python3 -m mypy .

# Frontend
cd frontend && npm run lint && npm run format:check && npx tsc --noEmit && npm run build
```

CI runs the same commands against the same pinned tool versions (see [`backend/pyproject.toml`](./backend/pyproject.toml), [`frontend/package.json`](./frontend/package.json), and [`.pre-commit-config.yaml`](./.pre-commit-config.yaml)). Bump tool versions in lockstep across all three surfaces.

## Documentation

Read in this order:

1. [`CLAUDE.md`](./CLAUDE.md) — project rules, tech stack, decision protocol. Read first every session.
2. [`ARCHITECTURE.md`](./ARCHITECTURE.md) — system design with reasoning.
3. [`ROADMAP.md`](./ROADMAP.md) — live progress tracker. Current phase, active task, blockers.
4. [`DECISIONS.md`](./DECISIONS.md) — architectural decisions log. Every D-NNN with rationale.
5. [`PRD.md`](./PRD.md), [`SCHEMA.md`](./SCHEMA.md), [`PROMPTS.md`](./PROMPTS.md), [`AGENTS.md`](./AGENTS.md), [`EVALS.md`](./EVALS.md), [`COSTS.md`](./COSTS.md), [`AI_STRATEGY.md`](./AI_STRATEGY.md), [`VISION.md`](./VISION.md), [`STACK.md`](./STACK.md), [`FLOWS.md`](./FLOWS.md), [`TRAINING.md`](./TRAINING.md), [`MCP.md`](./MCP.md) — domain-specific deep dives.

## Audit & cleanup

[`AUDIT_REPORT.md`](https://github.com/aidn31/tex-v2/blob/chore/repo-audit/AUDIT_REPORT.md) (on the `chore/repo-audit` branch) lists the open repo hygiene findings and which PRs have closed them.

## License

Proprietary. All rights reserved.
