# STACK.md — TEX v2

Complete tool inventory. Every layer. Every version. Every configuration decision.
Read this before installing anything, writing any configuration, or making any
infrastructure decision. The stack is locked. Deviations require Tommy's explicit
approval and a DECISIONS.md entry.

---

## STACK OVERVIEW

```
Layer               Tool                       Version       Role
────────────────────────────────────────────────────────────────────────────────────────────
Frontend            Next.js                    15.x          App Router. UI and routing.
React               react / react-dom          19.x          UI runtime.
Styling             Tailwind CSS               3.x           Utility classes. Not used in PDF.
Auth                Clerk (@clerk/nextjs)      5.x           JWTs, user lifecycle, webhooks.
Payments (front)    @stripe/stripe-js          4.x           Stripe.js loader; reserved (server-side checkout only today).
Frontend Deploy     Vercel                     —             Auto-deploy from main. Preview from branches.
Product Analytics   posthog-js                 1.x           Installed; deferred to Phase 5 (Issue #29).
Frontend lint       eslint                     9.39.4        Flat config via @eslint/eslintrc shim.
                    typescript-eslint          8.59.3        Pinned in package.json.
                    eslint-config-next         15.5.18       Matches Next major.
Frontend format     prettier                   3.8.3         Pre-commit + CI.
────────────────────────────────────────────────────────────────
Backend             FastAPI                    0.115.*       HTTP API. Validates, routes, enqueues.
ASGI server         uvicorn[standard]          0.32.*        Production process.
Language            Python                     3.12          Workers and API. Same version everywhere.
Task Queue          Celery                     5.4.*         4 queues. Chord for parallel sections.
Message Broker      redis (client)             5.2.*         Celery broker + result backend.
Message Broker srv  Redis                      7-alpine      Local; managed Redis in prod.
DB driver           psycopg2-binary            2.9.*         Raw SQL only.
Validation          Pydantic                   2.9.*         All request/response models.
JWT                 PyJWT                      2.9.*         Clerk JWT verification.
Crypto              cryptography               43.*          Backing for PyJWT.
HTTP client         httpx                      0.27.*        Async HTTP (Clerk JWKS, etc.).
Webhook signatures  svix                       1.40.*        Clerk Svix webhook verification (pinned — 1.64 incompatible with Pydantic 2.9).
PDF                 weasyprint                 62.*          Print-optimized PDF.
PDF (low-level)     pydyf                      0.11.*        Pinned — WeasyPrint 62.3 incompatible with pydyf 0.12.x.
Form parsing        python-multipart           0.0.*         FastAPI form data.
Local dev .env      python-dotenv              1.*           Local dev only.
Error tracking      sentry-sdk[fastapi]        2.*           Installed; deferred to Phase 5 (Issue #29).
APM                 ddtrace                    2.*           Datadog tracer; deferred to Phase 5 (Issue #29).
S3-compatible       boto3                      1.35.*        Cloudflare R2 access.
Backend lint        ruff                       0.15.13       Pre-commit + CI lint and format.
Backend types       mypy                       2.1.0         Pre-commit + CI typecheck (strict=false baseline).
────────────────────────────────────────────────────────────────
Database            Neon PostgreSQL            16            Raw SQL. No ORM. Fresh connection per call.
Film Storage        Cloudflare R2              —             S3 API via boto3. Two buckets: films + reports.
Container Registry  GCP Artifact Registry      —             Docker images for all Cloud Run services.
Backend Deploy      Google Cloud Run           —             5 services. See CLOUD RUN section.
Containerization    Docker                     26.x          Same Dockerfile, different CMD per service.
CI                  GitHub Actions             —             Lint + typecheck + build on every PR.
────────────────────────────────────────────────────────────────
AI SDK              google-genai               >=1.0,<2.0    Gemini Developer API + Vertex (current SDK).
AI SDK (Vertex)     google-cloud-aiplatform    >=1.71,<2.0   Vertex AI client (active when GEMINI_BACKEND=vertex).
File storage (Vrtx) google-cloud-storage       >=2.18,<3.0   GCS uploads (active when GEMINI_BACKEND=vertex).
AI — Sections 1-4   Gemini 2.5 Pro             —             Text input from synthesis_document (synthesis-only mode, D-024).
AI — Prompt 0A      Gemini 2.5 Pro             —             Video input per chunk (extract_chunk).
AI — Prompt 0B      Gemini 2.5 Flash           —             Text input (run_chunk_synthesis).
AI — Sections 5-6   Gemini 2.5 Flash           —             Text input.
AI — Fallback (5-6) Claude 3.5 Sonnet          —             anthropic 0.36.*. Auto-triggers when Flash fails (logging deferred — Issue #27).
────────────────────────────────────────────────────────────────
Future (not v1):
Vector DB           pgvector (Neon)            installed     Installed at migration 015. Not queried.
Search              Typesense                  —             Not yet. Phase 3+.
Orchestration       LlamaIndex                 —             Not yet. Phase 3+.
```

**Canonical prompt versions: 0A v1.6, 0B v1.6 (see PROMPTS.md).**

---

## FRONTEND

### Next.js 15 — App Router

App Router only. No Pages Router. App Router is required for Server Components and is the
default in Next 15.

```
Directory structure:
frontend/app/
  (auth)/sign-in/[[...sign-in]]/page.tsx    — Clerk-hosted sign-in
  (auth)/sign-up/[[...sign-up]]/page.tsx    — Clerk-hosted sign-up
  dashboard/page.tsx                         — Coach home: teams, recent films, inline notifications
  teams/[id]/page.tsx                        — Team page: roster, films, reports (tabs)
  reports/[id]/page.tsx                      — Report status + PDF download (polls every 10s)
  upload/page.tsx                            — Film upload flow (single presigned PUT)
  admin/page.tsx                             — Corrections (admin home; is_admin-gated)
  admin/patterns/page.tsx                    — Pattern analyzer
  admin/users/page.tsx                       — User management
  page.tsx                                   — Root redirect
```

No `components/` subdirectory exists today. Page-level files only. `lib/api.ts` holds all
typed fetch wrappers; there is no separate `lib/clerk.ts`.

**Critical Next.js config (`next.config.js`):**

```js
module.exports = {
  output: 'standalone',          // required for Docker / Cloud Run builds
}
```

That is the entire file. No `experimental.serverActions` override.

### Tailwind CSS 3

Theme locked at `frontend/tailwind.config.js`:

```js
theme: {
  extend: {
    colors: {
      brand: '#F97316',      // orange — primary actions, active states
      background: '#0a0a0a', // near-black — page background
      surface: '#141414',    // dark card/panel background
      border: '#262626',     // subtle borders
    }
  }
}
```

WeasyPrint does not use Tailwind. The PDF has its own static stylesheet at
`backend/templates/report.css`. Tailwind classes in any WeasyPrint template would render
as unstyled text — WeasyPrint has no PostCSS pipeline.

### Clerk (frontend + webhooks)

Auth provider. Handles signup, login, session management, and user webhooks. Clerk issues
JWTs; FastAPI verifies them. No server-side session store.

```ts
// frontend/middleware.ts
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server'

const isPublic = createRouteMatcher(['/sign-in(.*)', '/sign-up(.*)'])

export default clerkMiddleware((auth, req) => {
  if (!isPublic(req)) auth().protect()
})
```

**Clerk webhooks** (`user.created`, `user.deleted`) hit `POST /webhooks/clerk` with Svix
signature verification. `user.created` → INSERT INTO users. `user.deleted` → set
`users.deleted_at`. In local dev, the outbound webhook is unreliable through ngrok, so
`POST /dev/seed-user` (in `routers/dev.py`) acts as a stand-in — the dashboard calls it
on mount in development mode.

### Stripe (server-side checkout only today)

Payment processing. Hosted Checkout sessions. The frontend never touches card data.

```
TEX uses:
  stripe.checkout.Session.create()     hosted checkout URL — mode="payment" only
  stripe.Webhook.construct_event()     verifies + parses webhook payloads
  Event: checkout.session.completed    the only event TEX acts on today

TEX does NOT use:
  Stripe Elements                      hosted checkout is sufficient
  Stripe Billing / subscriptions       pay-per-report at launch — see Issue #30
  Stripe Connect                       not a marketplace
```

**Stripe products (configured in Stripe Dashboard, not in code):**

```
STARTER     $49.00 USD one-time     STRIPE_REPORT_PRICE_ID  (wired)
```

Two additional env vars exist as placeholders:

```
STRIPE_COACH_PRICE_ID                 reserved — no subscription checkout path built (Issue #30)
STRIPE_PROGRAM_PRICE_ID               reserved — no subscription checkout path built (Issue #30)
```

These are documented in `backend/.env.example` for future use; they are not referenced
anywhere in code today.

**Webhook signature verification — mandatory:**

```python
event = stripe.Webhook.construct_event(
    payload=await request.body(),
    sig_header=request.headers["stripe-signature"],
    secret=os.environ["STRIPE_WEBHOOK_SECRET"],
)
# If this raises, return 400 immediately. Never process an unsigned event.
```

**Stripe webhook path:** `POST /stripe/webhook` (not `/webhooks/stripe` — the Stripe router
is mounted under `/stripe`).

### Vercel

Frontend deploy. Automatic on merge to `main`. Preview deploys on every feature branch.

**Required Vercel environment variables (production):**

```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
CLERK_SECRET_KEY
NEXT_PUBLIC_API_BASE_URL              # Cloud Run tex-api service URL
```

Reserved (not currently wired):

```
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY    # uncommented in frontend/.env.example as reserved
NEXT_PUBLIC_POSTHOG_KEY               # uncommented in frontend/.env.example as reserved
```

`NEXT_PUBLIC_*` variables are exposed to the browser. Every other variable is server-only.
Never put a secret in a `NEXT_PUBLIC_` variable.

### PostHog — installed, deferred to Phase 5 (Issue #29)

`posthog-js` is declared in `frontend/package.json` but **not initialized** anywhere in
the app. Event-tracking wiring is part of the Phase 5 observability work tracked in Issue
#29. The intended event list (`film_uploaded`, `report_generation_started`, etc.) is in
ARCHITECTURE.md but not yet implemented.

---

## BACKEND

### FastAPI 0.115

HTTP API layer. No business logic — FastAPI validates, authenticates, enqueues. Workers
do the work.

**App startup — lifespan events (`backend/main.py`):**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_env()
    yield

app = FastAPI(lifespan=lifespan)
```

`validate_env()` checks the **infrastructure vars only**: `NEON_*`, `REDIS_URL`,
`GEMINI_API_KEY`. Service vars (Stripe, Clerk, R2, Anthropic) are validated lazily on
first use. The original "every var in .env.example is checked at boot" rule was relaxed
during Phase 2 because some service keys are not required for every code path.

**Router registration (`backend/main.py`):**

```python
app.include_router(films.router,         prefix="/films",         tags=["films"])
app.include_router(reports.router,       prefix="/reports",       tags=["reports"])
app.include_router(teams.router,         prefix="/teams",         tags=["teams"])
app.include_router(roster.router,        prefix="/roster",        tags=["roster"])
app.include_router(webhooks.router,      prefix="/webhooks",      tags=["webhooks"])      # Clerk
app.include_router(stripe.router,        prefix="/stripe",        tags=["stripe"])        # Stripe (separate from Clerk webhooks)
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
app.include_router(admin.router,         prefix="/admin",         tags=["admin"])
app.include_router(dev.router,           prefix="/dev",           tags=["dev"])           # local-dev only
```

All routes are protected by Clerk JWT verification except `/webhooks/*` and `/stripe/webhook`
(protected by provider signatures) and `/dev/*` (gated by environment).

**Admin routes** additionally check `is_admin` via a live DB query on every request
(`services/clerk.py::require_admin`), not from a cache or the JWT.

### Python 3.12

Pinned in `backend/Dockerfile`:

```dockerfile
FROM python:3.12-slim
```

3.12 is required. Not 3.11. Not 3.10. Same version in the FastAPI container and all Celery
worker containers. Mixing Python versions across services causes subtle dependency conflicts.

**Required system packages (`backend/Dockerfile`):**

```dockerfile
RUN apt-get update && apt-get install -y \
    ffmpeg \           # film processing
    libpango-1.0-0 \   # WeasyPrint PDF rendering
    libpangoft2-1.0-0 \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*
```

FFmpeg includes FFprobe. WeasyPrint requires `libpango` system packages — missing them
produces malformed PDFs silently.

**Empirical note:** FFmpeg compression runs ~10× slower in Docker for Mac than native
(no VideoToolbox hardware acceleration inside the Linux VM). Production Cloud Run does
not have this issue. The `process_film` task uses a 120-minute hard timeout (D-026) to
accommodate the Docker dev case.

**Python dependencies (`backend/requirements.txt` — current pins):**

```
fastapi==0.115.*
uvicorn[standard]==0.32.*
celery[redis]==5.4.*
redis==5.2.*
psycopg2-binary==2.9.*
pydantic==2.9.*
google-genai>=1.0,<2.0                    # Gemini SDK (replaces deprecated google-generativeai)
google-cloud-aiplatform>=1.71,<2.0        # Vertex AI client
google-cloud-storage>=2.18,<3.0           # GCS uploads (Vertex backend)
anthropic==0.36.*                          # Claude fallback for sections 5-6
stripe==11.*
clerk-backend-api==1.*
svix==1.40.*                               # pinned — 1.64 incompatible with Pydantic 2.9
weasyprint==62.*
pydyf==0.11.*                              # pinned — WeasyPrint 62.3 incompatible with pydyf 0.12.x
boto3==1.35.*                              # Cloudflare R2
sentry-sdk[fastapi]==2.*                   # installed; not initialized (Issue #29)
ddtrace==2.*                               # Datadog APM; not initialized (Issue #29)
python-multipart==0.0.*                    # FastAPI form data
python-dotenv==1.*                         # local dev only
PyJWT==2.9.*                               # Clerk JWT verification
cryptography==43.*
httpx==0.27.*
```

Pin to minor versions (`0.115.*`), not patch. The `svix` and `pydyf` exact-minor pins are
not arbitrary — both have specific incompatibilities with other libraries in the stack.
Do not loosen those pins without testing.

### Celery 5 + Redis 7

Celery is the task queue. Redis is the broker (message bus) and result backend. Redis
stores nothing else — no application state, no session data, no cache.

**Celery app configuration (`backend/tasks/celery_app.py`):**

```python
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,       # status=STARTED in Redis as soon as a worker picks up
    task_acks_late=True,           # ack after completion, not on receipt (crash-safe)
    worker_prefetch_multiplier=1,  # one task per slot — prevents long-task hostage
    broker_transport_options={
        "visibility_timeout": 10800,  # 3h; must exceed longest hard time_limit (process_film @ 7200s)
    },
    task_default_queue="notifications",  # fail-safe default
)
```

These are reliability tunings, not performance knobs. Changing any of them changes the
failure mode of the entire pipeline. See AGENTS.md for the full rationale on each setting.

**Queue definitions:**

```python
from kombu import Queue

celery_app.conf.task_queues = (
    Queue("film_processing"),
    Queue("report_generation"),
    Queue("section_generation"),
    Queue("notifications"),
)
```

**Timeout values (authoritative source is AGENTS.md):**

```
Queue                 soft_time_limit   time_limit    concurrency
─────────────────────────────────────────────────────────────────
film_processing       117 min (7000s)   120 min       1
report_generation     25 min  (1500s)   30 min        1
section_generation    8 min   (480s)    10 min        4
notifications         25 sec            30 sec        2
```

`film_processing` is 120 min (D-026) to accommodate Docker-for-Mac FFmpeg slowness.

### Redis 7 — Configuration

Used only as Celery broker and result backend.

**Mandatory configuration:**

```
appendonly yes              # AOF persistence — survives clean restarts
appendfsync everysec        # flush to disk every second
maxmemory 512mb             # set a limit
maxmemory-policy allkeys-lru
```

AOF protects against clean restarts. The DB-based startup recovery function in every
worker handles the case where AOF itself is corrupted or replaced.

**Connection string format:**

```
REDIS_URL=redis://:password@hostname:6379/0
```

Use database index 0 for Celery. Do not share index 0 with any other use.

### WeasyPrint 62 (+ pydyf 0.11)

HTML → PDF conversion. Python-native. No headless browser.

**HTML is built inline in `backend/services/pdf.py::_build_html()`.** There is **no**
`report.html` template file. The only template asset on disk is
`backend/templates/report.css`, the print stylesheet.

**Why WeasyPrint instead of Puppeteer/Playwright:** No headless Chrome install, no
browser process, no JavaScript execution surface in a worker handling coach data.
WeasyPrint implements CSS print rules directly — more predictable pagination on a static
print template.

**Invocation pattern (`backend/services/pdf.py`):**

```python
def assemble_pdf(sections: dict, team_name: str, report_date: str, is_partial: bool) -> bytes:
    html_content = _build_html(sections, team_name, report_date, is_partial)
    css = CSS(filename=str(CSS_PATH))   # backend/templates/report.css
    return HTML(string=html_content).write_pdf(stylesheets=[css])
```

`write_pdf()` returns bytes directly. Stream those bytes to R2 — don't write to disk and
read back.

---

## DATABASE — Neon PostgreSQL 16

### Connection Model

```python
# backend/services/db.py — the entire database layer
def get_connection():
    return psycopg2.connect(
        host=os.environ["NEON_HOST"],
        database=os.environ["NEON_DB"],
        user=os.environ["NEON_USER"],
        password=os.environ["NEON_PASSWORD"],
        sslmode="require",
        connect_timeout=10,
    )
```

Open → execute → close. Every call. No connection pooling at the application layer.
No SQLAlchemy connection pool. No persistent connection objects.

### SQL Rules

- Raw SQL only. No SQLAlchemy. No Tortoise. No Prisma.
- Parameterized queries only — `%s` placeholders. No string interpolation into SQL.
- Every query on a user-facing table includes `WHERE user_id = %s`.
- `user_id` always comes from `verify_clerk_jwt()`. Never from the request body.

### Migrations

Numbered raw SQL files in `backend/migrations/`. Applied in order by `scripts/migrate.py`.

```
001_create_users.sql
002_create_teams.sql
003_create_roster_players.sql
004_create_films.sql
005_create_film_chunks.sql
006_create_reports.sql
007_create_report_films.sql
008_create_report_sections.sql
009_create_corrections.sql
010_create_film_analysis_cache.sql
011_create_dead_letter_tasks.sql
012_create_notifications.sql
013_create_payments.sql
014_create_fallback_events.sql            # reserved — writes deferred per Issue #27
015_install_pgvector.sql                  # pgvector extension installed; not queried yet
016_add_film_chunks_extraction.sql        # Prompt 0A output columns
```

Apply to Neon dev branch first. Promote to production only after testing on dev.
SCHEMA.md is the column-by-column source of truth.

### pgvector

Installed at migration 015. Not queried in v1. The extension is installed now so Phase 3+
work (player embeddings) adds columns without an extension migration.

---

## FILE STORAGE — Cloudflare R2

### Two Buckets

```
tex-films-{env}     — raw uploads + FFmpeg chunks. private. no public access.
tex-reports-{env}   — generated PDF reports. private. no public access.
```

`{env}` is `dev` or `prod`. Never share buckets between environments.

### Access Pattern

All access via presigned URLs. The browser never sees R2 credentials. FastAPI generates
presigned URLs. R2 credentials live only in Cloud Run secrets.

```python
# backend/services/r2.py
def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{os.environ['CLOUDFLARE_R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
        aws_access_key_id=os.environ["CLOUDFLARE_R2_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["CLOUDFLARE_R2_SECRET_ACCESS_KEY"],
        region_name="auto",
    )
```

**Presigned URL expiry:**

```
Upload URLs    1 hour (3600s)    Large films on slow connections
Download URLs  15 min (900s)     Coach clicks download, short-lived URL
```

**R2 key naming:**

```
films/{user_id}/{film_id}/{original_filename}          # raw upload. permanent.
chunks/{film_id}/chunk_{index:03d}.mp4                 # FFmpeg chunks. deleted after reports.status=complete.
reports/{user_id}/{report_id}/scouting_report.pdf      # final PDF. permanent.
```

R2 chunks are deleted only after `reports.status` is written terminal. R2 is the
re-upload source when Gemini File API URIs expire (Developer API backend only — Vertex/GCS
files do not expire).

---

## AI PROVIDERS

### Stage-to-model assignment (canonical)

```
STAGE                        MODEL              INPUT SHAPE
──────────────────────────────────────────────────────────────────────
Prompt 0A (extract_chunk)    Gemini 2.5 Pro     Chunk video (per chunk, one call per chunk)
Prompt 0B (run_chunk_synth)  Gemini 2.5 Flash   Text — all 0A outputs + roster
Section 1-4 (run_section)    Gemini 2.5 Pro     Text — synthesis_document (synthesis-only mode)
Section 5-6 (run_synth_sec)  Gemini 2.5 Flash   Text — sections 1-4 output (sequential)
Fallback for 5-6             Claude 3.5 Sonnet  Text — same as Flash, auto-triggers on Flash failure
```

Sections 1-4 use Pro on text input. A future Pro→Flash evaluation for those sections is
an eval-harness question, not a current cost-driven switch. Synthesis-only mode (D-024)
defines the input shape (text, not video); model choice is independent.

**Canonical prompt versions: 0A v1.6, 0B v1.6 (see PROMPTS.md).**

### Gemini SDK (`google-genai`)

```python
# backend/services/ai/gemini.py
from google import genai
from google.genai import types

# 5-minute HTTP timeout — required.
# SDK default (~60s) is too short for Prompt 0A on long chunks and Prompt 0B on large
# concatenated input. Without this override, RemoteDisconnected burns retries silently.
client = genai.Client(http_options=types.HttpOptions(timeout=300_000))  # ms

PRO_MODEL   = "gemini-2.5-pro"
FLASH_MODEL = "gemini-2.5-flash"
```

The old `google-generativeai` SDK is **deprecated** — do not re-add it. The current SDK
is `google-genai>=1.0,<2.0`.

**Dual-backend support — Developer API + Vertex AI:**

```
GEMINI_BACKEND=developer_api    Gemini File API (48-hour expiry, expiry-aware re-upload from R2)
GEMINI_BACKEND=vertex           Vertex AI + GCS storage (no expiry, no re-upload scan)
```

Both backends are wired and tested. See D-018 for the Vertex migration history.

Per D-024, `create_context_cache()` does **not** call Google's CachedContent API at
report-generation time. It returns a local `vertex:no-cache:<json>` sentinel string
encoding the text payload sections 1-4 will receive. The Gemini File API / GCS upload
happens during `extract_chunk` (for Prompt 0A), not during report generation.

**Rate limiting — Redis token bucket (every Gemini call acquires a slot):**

```python
# backend/services/rate_limit.py
RATE_LIMITS = {
    "gemini-2.5-pro":    3,   # requests per 60s
    "gemini-2.5-flash": 15,   # requests per 60s
    "gemini-file-api": 10,    # requests per 60s — separate bucket for File API uploads
}
```

The three buckets are independent. Sharing the file-API bucket with a prompt bucket would
under-utilize quota and slow Prompt 0A throughput. Every Gemini call acquires the
appropriate slot before executing.

### Claude 3.5 Sonnet — sections 5-6 fallback only

`backend/services/ai/anthropic.py` implements only `analyze_text()`. `analyze_video()`,
`analyze_video_cached()`, `create_context_cache()`, and `delete_context_cache()` raise
`NotImplementedError` — Claude is used solely as the sections 5-6 text fallback.

**Fallback path:** `_run_text_section` (in `tasks/report_generation.py`) catches the Flash
exception and silently invokes Claude via `get_fallback_provider()`. The `fallback_events`
table exists in the schema but is **not written** by application code today — see Issue
#27 for the decision to wire writes or drop the table.

### AI Provider Abstraction

Nothing in TEX outside of `services/ai/` imports a provider class. All calls go through
`services/ai/router.py`:

```python
def get_ai_provider() -> AIVideoProvider:
    provider = os.environ.get("AI_VIDEO_PROVIDER", "gemini")
    if provider != "gemini":
        raise ValueError(f"Unknown AI provider: {provider}")
    from services.ai.gemini import GeminiProvider
    return GeminiProvider()

def get_fallback_provider() -> AIVideoProvider:
    # Hardcoded for sections 5-6 text fallback. Not env-configurable.
    from services.ai.anthropic import ClaudeProvider
    return ClaudeProvider()
```

`openai.py` was sketched in earlier doc revisions but does not exist on disk. The router
accepts `"gemini"` only and raises on anything else. ARCHITECTURE.md AI PROVIDER
ABSTRACTION section has the full rationale.

---

## INFRASTRUCTURE

### Google Cloud Run — 5 Services

Each service is a separate Docker image built from the same `backend/` directory with
different entry points. One Dockerfile (CMD not set; specified per Cloud Run service).

```
Service Name            Queue                 CMD                                          min  max  memory   /tmp
──────────────────────────────────────────────────────────────────────────────────────────────────────────────────
tex-api                 —                     uvicorn main:app --host 0.0.0.0 --port 8080  1    10   2Gi      512MB
tex-worker-film         film_processing       celery -A tasks.celery_app worker            0    5    8Gi      8GB
                                              -Q film_processing --concurrency=1
tex-worker-report       report_generation     celery -A tasks.celery_app worker            0    3    2Gi      512MB
                                              -Q report_generation --concurrency=1
tex-worker-section      section_generation    celery -A tasks.celery_app worker            0    10   2Gi      512MB
                                              -Q section_generation --concurrency=4
tex-worker-notify       notifications         celery -A tasks.celery_app worker            0    3    512Mi    512MB
                                              -Q notifications --concurrency=2
```

`tex-worker-film` requires `--execution-environment=gen2` and `--ephemeral-storage=8Gi` —
the default 512MB /tmp is exceeded by a 2-hour film compressed to 720p alone.
`tex-api` has `min-instances=1` to avoid cold starts on every request. Workers scale to 0.

### Docker

Single `Dockerfile` at `backend/Dockerfile`. CMD set per Cloud Run service (see Dockerfile
comments). Tag images by commit SHA — never rely on `latest` alone.

### GitHub Actions — CI

Two CI workflows run on every pull request to `main`. There is **no auto-deploy workflow
in the repo today**; deploys are manual (`gcloud run deploy`).

```
.github/workflows/backend.yml      # ruff lint + ruff format check + mypy + py_compile
.github/workflows/frontend.yml     # eslint + prettier --check + tsc --noEmit + next build
.github/workflows/gitleaks.yml     # secret scan on every PR
```

All three are required status checks for merging to `main` (branch protection, D-020).
`enforce_admins: true` — admins cannot bypass.

### Repository Hygiene Infrastructure

Five infrastructure PRs landed during Phase 0 cleanup; current state on `main`:

```
.pre-commit-config.yaml              gitleaks, ruff, mypy, eslint, prettier,
                                     trailing-whitespace, end-of-file-fixer,
                                     check-merge-conflict, check-added-large-files (500KB)
.github/dependabot.yml               weekly pip + npm + github-actions bumps
.github/pull_request_template.md     short checklist on every PR
backend/pyproject.toml               ruff (E/F/W/I/UP/B) + mypy config (strict=false baseline)
frontend/eslint.config.mjs           ESLint 9 flat config + FlatCompat shim for eslint-config-next
README.md                            repo front door — pointer to canonical docs
```

Tooling versions are pinned identically across `pre-commit-config.yaml` and CI workflow
files. See D-019, D-020, D-021, D-022 for adoption history.

### Secrets Management

**Backend secrets:** Google Cloud Secret Manager. Cloud Run reads secrets as env vars at boot.
**Frontend secrets:** Vercel environment variables (encrypted at rest).
**Local dev:** `backend/.env` (gitignored). `.env.example` documents every required variable.

GitHub secret scanning + push protection are enabled at the repo level. gitleaks runs
pre-commit and in CI. Three independent layers of secret-leak prevention.

---

## OBSERVABILITY — INSTALLED, DEFERRED TO PHASE 5 (ISSUE #29)

All three observability tools are dependencies but **not initialized in code today**:

```
Tool       Dependency installed in        Env var reserved in            Initialized?
─────────────────────────────────────────────────────────────────────────────────────
Sentry     backend/requirements.txt       SENTRY_DSN (backend/.env)      No
Datadog    backend/requirements.txt       DATADOG_API_KEY (backend/.env) No
PostHog    frontend/package.json          NEXT_PUBLIC_POSTHOG_KEY        No
                                          (reserved in .env.example)
```

References in AGENTS.md to "set Sentry context on every task" and in ARCHITECTURE.md to
`tex.*` Datadog metrics describe the **target** wiring, not the running implementation.
Phase 5 production hardening wires these — tracked in **GitHub Issue #29**.

---

## LOCAL DEVELOPMENT

```yaml
# docker-compose.yml — no `version:` key (removed; modern Compose ignores it)
services:
  api:
    build: ./backend
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ports: ["8001:8000"]              # host 8001 (host 8000 was in use locally)
    env_file: ./backend/.env
    volumes: ["./backend:/app"]
    depends_on: [redis]

  worker:
    build: ./backend
    command: celery -A tasks.celery_app worker -Q film_processing,report_generation,section_generation,notifications --concurrency=2 --loglevel=info
    env_file: ./backend/.env
    volumes: ["./backend:/app"]
    depends_on: [redis]

  redis:
    image: redis:7-alpine
    ports: ["6380:6379"]              # host 6380 (host 6379 was in use locally)
    command: redis-server --appendonly yes
```

**Frontend runs outside Docker in local dev:**

```bash
cd frontend && npm run dev    # http://localhost:3000
```

Frontend `.env.local` should set `NEXT_PUBLIC_API_BASE_URL=http://localhost:8001` (matching
the docker-compose host port remap above).

**No local Neon.** Use Neon's dev branch feature — branches are isolated from production
and reset independently.

---

## ENVIRONMENT VARIABLE REFERENCE

Backend (`backend/.env.example`):

```
# Neon PostgreSQL
NEON_HOST=
NEON_DB=
NEON_USER=
NEON_PASSWORD=

# Redis
REDIS_URL=redis://:password@localhost:6379/0

# AI Providers
GEMINI_API_KEY=
ANTHROPIC_API_KEY=
AI_VIDEO_PROVIDER=gemini
GEMINI_BACKEND=developer_api

# Cloudflare R2
CLOUDFLARE_R2_ACCOUNT_ID=
CLOUDFLARE_R2_ACCESS_KEY_ID=
CLOUDFLARE_R2_SECRET_ACCESS_KEY=
CLOUDFLARE_R2_BUCKET_FILMS=tex-films-dev
CLOUDFLARE_R2_BUCKET_REPORTS=tex-reports-dev

# Auth
CLERK_SECRET_KEY=
CLERK_WEBHOOK_SECRET=

# Payments
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_REPORT_PRICE_ID=          # STARTER tier — wired
STRIPE_COACH_PRICE_ID=           # reserved — no subscription path (Issue #30)
STRIPE_PROGRAM_PRICE_ID=         # reserved — no subscription path (Issue #30)

# Observability (deferred — Issue #29)
SENTRY_DSN=
DATADOG_API_KEY=

# App
ENVIRONMENT=development          # "development" | "production"
FRONTEND_URL=http://localhost:3000
BASE_URL=http://localhost:3000
```

Frontend (`frontend/.env.example`):

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8001
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=

# Reserved — uncommented when wired:
# NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=
# NEXT_PUBLIC_POSTHOG_KEY=
# NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
```

`validate_env()` only checks `NEON_*`, `REDIS_URL`, and `GEMINI_API_KEY` at boot. Service
vars are validated lazily on first use.

---

## WHAT IS NOT IN THE STACK YET

Do not build, install, or configure any of the following until the relevant phase is ready.

```
Typesense                — full-text search. Phase 3.
LlamaIndex / LangChain   — RAG orchestration. Phase 3.
pgvector queries         — extension installed at migration 015; no queries until embeddings exist.
Fine-tuning              — Phase 4. Not before 1,000+ labeled corrections.
WebSockets               — not needed. Polling every 10s is sufficient for 15-45 minute jobs.
GraphQL                  — not needed. REST over FastAPI is the correct level.
Kubernetes               — not needed. Cloud Run with Celery handles the workload.
Stripe subscriptions     — Coach / Program tiers tracked in Issue #30.
Automated deploy CI      — manual gcloud deploys today. CI runs lint/typecheck/build only.
Orphaned-file purge job  — described in ARCHITECTURE.md GEMINI FILE API INTEGRATION; not built.
```

---

*Last updated: 2026-05-19 — Full rewrite for synthesis-only mode (D-024). SDK migrated to*
*google-genai. Vertex/GCS dual-backend documented as current. Observability tools marked*
*deferred (Issue #29). Subscription tiers stripped (Issue #30). Batch API routing removed*
*(not built). Hygiene infrastructure (gitleaks/Dependabot/ruff/mypy/eslint/prettier/branch*
*protection/PR template) documented. Docker-compose ports + migration list + dependency*
*list all aligned to current code.*
*Stack version: v2.0.0*
