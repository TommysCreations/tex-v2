# TEX v2 — Canonical Doc Drift Report

**Date:** 2026-05-19
**Scope:** STACK.md, ARCHITECTURE.md, SCHEMA.md, FLOWS.md, PROMPTS.md, AGENTS.md, EVALS.md, COSTS.md
**Method:** Each doc read in full, then compared against the corresponding code, configs, migrations, and prompt files. Read-only analysis — no doc or code was modified.

---

## STACK.md

**Status:** Significantly drifted

**What's accurate:**
- Next.js 15.x pin (`frontend/package.json:17` → `^15.0.0`).
- Tailwind 3.x pin + theme palette (`tailwind.config.js:7-10` — `brand: '#F97316'`, `background: '#0a0a0a'`, `surface: '#141414'`, `border: '#262626'` match exactly).
- FastAPI `0.115.*`, Python 3.12 (`backend/Dockerfile:1`), Celery `5.4.*`, Redis 7 (`docker-compose.yml:18`), WeasyPrint `62.*`, Pydantic `2.9.*`.
- Dockerfile system packages (`ffmpeg`, `libpango-1.0-0`, `libpangoft2-1.0-0`, `libffi-dev`) match `backend/Dockerfile:3-9`.
- `anthropic==0.36.*`, `stripe==11.*`, `clerk-backend-api==1.*`, `boto3==1.35.*`, `sentry-sdk[fastapi]==2.*`, `ddtrace==2.*`, `psycopg2-binary==2.9.*`, `redis==5.2.*`, `uvicorn[standard]==0.32.*` all match `backend/requirements.txt`.
- Frontend `output: 'standalone'` matches `next.config.js:4`.
- TypeScript strict mode + `@typescript-eslint/no-explicit-any: error` enforced (`tsconfig.json:7`, `eslint.config.mjs:34`).
- AOF persistence in dev Redis (`docker-compose.yml:20`).

**What's stale:**
- **Gemini SDK migrated.** `STACK.md:320` says `google-generativeai==0.8.*`; `backend/requirements.txt:7` is `google-genai>=1.0,<2.0` (CLAUDE.md explicitly forbids re-adding the old SDK). All code samples at `STACK.md:678,680,707-719` (`import google.generativeai as genai`, `genai.caching.CachedContent.create`) are obsolete — code uses `google-genai` + Vertex paths in `services/ai/gemini.py`.
- **`svix` pin** is `1.*` in doc (`STACK.md:324`) but actually pinned to `1.40.*` (`requirements.txt:13`). The Pydantic-2.9 compat reason (in CLAUDE.md) is not in STACK.md.
- **`pydyf==0.11.*` pin** (`requirements.txt:15`) entirely missing from STACK.md.
- **Local dev ports drifted.** `STACK.md:1011,1014,1025-1026` show api `8000:8000` and redis `6379:6379`; `docker-compose.yml:5,19` show `8001:8000` and `6380:6379`. `frontend/.env.example:7` correctly points at `8001`; STACK.md:1035 still says `8000`.
- **Migration list off-by-one+ from 003 onward.** STACK.md:560-574 has `003_create_films.sql ... 012_install_pgvector.sql`. Real order in `backend/migrations/` is `003_create_roster_players → 004_create_films → … → 015_install_pgvector → 016_add_film_chunks_extraction`. Doc missing `007_create_report_films`, `014_create_fallback_events`, `016_add_film_chunks_extraction` and uses wrong numbers.
- **`docker-compose.yml` `version:` key** referenced in STACK.md:1006 but removed from the actual file.
- **`next.config.js` shows `experimental.serverActions`** in STACK.md:71-79; real file only has `output: 'standalone'`.
- **`validate_env()` scope** — STACK.md:250-253 claims it checks every `.env.example` var; in practice (per `backend/.env.example` notes and CLAUDE.md) it only checks `NEON_* + REDIS_URL + GEMINI_API_KEY`.
- **Doc footer "Last updated: Phase 0 — Context Engineering"** (STACK.md:1118). Repo is in Phase 3 with Phase 4 code complete.

**What's missing:**
- The entire **5-PR hygiene audit** is invisible to this doc:
  - `gitleaks` pre-commit (`.pre-commit-config.yaml:21-24`) + CI workflow (`.github/workflows/gitleaks.yml`).
  - Dependabot (`.github/dependabot.yml`) — weekly bumps for pip / npm / github-actions.
  - Backend CI (`.github/workflows/backend.yml`) — ruff lint, ruff format check, mypy, byte-compile.
  - Frontend CI (`.github/workflows/frontend.yml`) — eslint, prettier check, `tsc --noEmit`, `next build`.
  - `STACK.md:903-938` shows a hypothetical `deploy.yml` with pytest + `gcloud run deploy` — that file does not exist.
  - Ruff (lint + format), Mypy, ESLint 9 flat config, Prettier, pre-commit framework — none mentioned.
  - PR template `.github/pull_request_template.md`, branch protection on main, repo `README.md` — none mentioned.
- **Tooling version pinning rule** ("must match exactly across pre-commit + CI", `backend/pyproject.toml:5-11`) is operational and undocumented.
- **Added Python deps** missing from STACK.md's requirements snippet: `PyJWT==2.9.*`, `cryptography==43.*`, `httpx==0.27.*`, `google-cloud-aiplatform>=1.71,<2.0`, `google-cloud-storage>=2.18,<3.0`.
- **Node version** — `.github/workflows/frontend.yml:41` uses Node 22; STACK.md never specifies one.
- **5-minute Gemini HTTP timeout override** (`services/ai/gemini.py::_get_dev_client`, `http_options=types.HttpOptions(timeout=300_000)`) — load-bearing bugfix, undocumented in STACK.md.
- **Vertex AI / GCS backend** is wired (not just future); STACK.md still presents it as "future flip".

**Recommended action:** Significant rewrite.

---

## ARCHITECTURE.md

**Status:** Significantly drifted

**What's accurate:**
- High-level system shape (Next.js → FastAPI on Cloud Run → Neon + Redis + R2) — correct.
- Provider-import discipline — only `services/ai/router.py:11-13` imports providers; every task uses `get_ai_provider()` / `get_fallback_provider()`.
- DB pattern: single `get_connection()` in `services/db.py`, raw SQL, open/execute/close in every task `finally`.
- Four Celery queues declared in `tasks/celery_app.py:35-40`.
- Idempotency status checks in every task (`film_processing.py:297`, `report_generation.py:194`, `section_generation.py:110`).
- Dead-letter table + writes, startup recovery (`celery_app.py:46-103`) with 2-hour film / 1-hour report thresholds.
- `film_chunks` table schema matches doc.
- `/tmp` cleanup with `film_id` prefix (`/tmp/{film_id}_raw{ext}`, `/tmp/{film_id}_chunk_%03d.mp4`); tracked + cleared in `finally`.
- FFmpeg compression threshold 1.8GB (`film_processing.py:369`); 25-min chunks via `segment_time=1500` (`services/ffmpeg.py:74-75`).
- FFprobe rules: 60s min, 10800s max, video stream required (`services/ffprobe.py:112-124`).
- URI expiry re-upload <1h window (`services/uri_expiry.py:16-57`).
- Sections 1-4 chord + 5-6 sequential callback with section-5 → section-6 context dependency (`report_generation.py:386-391, 791-810`).
- Claude fallback wired (`tasks/report_generation.py:578-599`); Claude raises `NotImplementedError` on video methods.
- Rate-limit buckets `gemini-2.5-pro` (3/min), `gemini-2.5-flash` (15/min), `gemini-file-api` (10/min) in `services/rate_limit.py:7-11`.
- Payment gate fires before report enqueue (`routers/reports.py:91-95`); free-first-report + credit + Stripe paths in `services/payment_gate.py`.
- Failure-credit logic in `_apply_failure_credit` (`report_generation.py:476`).
- Data isolation: `WHERE user_id = %s` everywhere; `require_admin` runs a DB read per request (`services/clerk.py:126-131`), not cached in JWT.
- Clerk Svix + Stripe webhook signatures verified before processing.
- PDF section order matches doc (`services/pdf.py:19-26`).
- R2 chunks deleted only after `reports.status` written terminal (`report_generation.py:1093-1105`).
- Prompt 0A wired into `extract_chunk` (`film_processing.py:613, 628`); atomic last-chunk handoff via `pg_try_advisory_xact_lock` (`film_processing.py:656-679`).
- Synthesis-only deviation acknowledged in a single paragraph at `ARCHITECTURE.md:686`.

**What's stale:**
- **The numbered report pipeline (~ARCHITECTURE.md:688-709)** still says step 4 creates a context cache "from chunk URIs + roster" and sections 1-4 receive the cache URI. In synthesis-only mode (`services/ai/gemini.py:7-26, 130-192`) `create_context_cache()` returns a `vertex:no-cache:<json>` sentinel and bundles only the synthesis document + roster as text. Sections 1-4 receive **text Parts only**, no video (`gemini.py:242-250`). The line-686 disclaimer is a band-aid; the numbered flow itself reads as old design.
- **PIPELINE INTELLIGENCE MAP (1141-1200)** — same problem; says sections 1-4 input is "cache URI (shared video + roster)". Reality: text-only.
- **"Context Caching Mandatory" cost block (1422-1469)** — the $18.92→$6.14 math assumes video tokens go to all 4 sections via cache. They don't. The framing is invalid.
- **Prompt 0B model** — ARCHITECTURE.md:400 says "Gemini 2.5 Pro". Code uses **Flash** (`film_processing.py:864` acquires `gemini-2.5-flash`, then `provider.analyze_text` → `GEMINI_FLASH_MODEL`).
- **`process_film` timeouts** — ARCHITECTURE.md:208-211 says soft 55min / hard 60min. Code is soft `7000s` / hard `7200s` (~117/120 min) at `film_processing.py:261-262`. The error string at lines 452, 458 still reads "55 minutes" — stale on both sides.
- **Stripe webhook path** — doc implies `/webhooks/stripe`; reality is `/stripe/webhook` (`main.py:58` mounts `stripe.router` at `/stripe`; `routers/stripe.py:160` declares `/webhook`).
- **PDF template path** — ARCHITECTURE.md:834 says `backend/templates/report.html` exists. It doesn't. Only `templates/report.css`; HTML is built inline in `services/pdf.py:_build_html` (lines 49-100).
- **Frontend upload flow** — doc describes multipart with `part_urls` / `parts` (ARCHITECTURE.md:869-875). Code uses single presigned PUT (`routers/films.py:38-85`, `frontend/app/upload/page.tsx:70`). No multipart endpoints exist.
- **AI router options** — ARCHITECTURE.md:1083-1091 shows `openai` and `anthropic` branches; `services/ai/router.py:22-25` only accepts `gemini` and raises `ValueError` otherwise.
- **`services/ai/openai.py` stub** — ARCHITECTURE.md:91, 1033 says it exists. It doesn't.
- **`services/ffmpeg.py` surface** — doc names `split_film_into_chunks()`, `get_duration()`, `compress_for_upload()`; real names are `compress_film` and `split_film`; `get_duration` lives in `services/ffprobe.py`.
- **`fallback_events` writes** — ARCHITECTURE.md:1242-1245 claims every Claude fallback writes a row and emits a Datadog metric. Table exists (`migrations/014_create_fallback_events.sql`) but **no code writes to it** (`report_generation.py:578-600` only logs).
- **Layer 2 upload validation** — ARCHITECTURE.md:477-494 says `validate_upload_request()` runs server-side before any presigned URL is issued. `routers/films.py:38-85` only checks team ownership; no extension/size validation. Layer 1 (frontend) only checks 4 MIME types, no size ceiling/floor.
- **Stripe checkout flow** — doc shows `POST /reports` returning checkout URL inline. Reality is two-step: `POST /reports` returns `payment_required=True` (`reports.py:92-93`), then frontend calls separate `POST /stripe/create-checkout-session` (`stripe.py:21`). Metadata field names also differ (`tex_user_id`, `tex_team_id`, `tex_film_ids` vs doc's `user_id`, `report_request`).
- **"Auto-trigger report after synthesis"** — doc (and CLAUDE.md product flow step 8) implies `run_chunk_synthesis` enqueues a pending report. Code never calls `generate_report.delay` from `film_processing.py`. Reports are only enqueued by `POST /reports` (free/credit) or the Stripe webhook (paid).
- **Frontend `components/upload/`, `components/report/`, `components/ui/`** (ARCHITECTURE.md:853-856) — none of these directories exist; only page-level files.
- **`frontend/lib/clerk.ts`** (ARCHITECTURE.md:859) — doesn't exist. Only `lib/api.ts`.

**What's missing:**
- **`backend/services/payment_gate.py`** — central decision function not in services list.
- **`backend/services/uri_expiry.py`** — extracted module; doc still shows the logic inline in `generate_report`.
- **`backend/services/gemini_files.py`** — Gemini-file upload/delete/poll module (Developer API + Vertex/GCS).
- **`backend/services/prompt_versions.py`** — `get_film_analysis_cache_prompt_version()` derives composite cache key `{sections_v}|{preprocess_v}` from prompt-file headers; this is now the canonical cache-invalidation source.
- **`backend/services/prompts.py`** — `VERSION:` + `---` loader; file format never documented.
- **`backend/services/roster_format.py`** — used by `extract_chunk` and `generate_report` to inject roster context.
- **`backend/services/film_cache.py`** — present, undocumented.
- **`backend/services/stripe_client.py`** — `configure_stripe()` + `verify_webhook()`; doc treats Stripe as router-only.
- **`backend/routers/dev.py`** — `/dev/seed-user` replaces Clerk webhook locally.
- **`backend/routers/notifications.py`** — separate router; not in routers list.
- **`backend/routers/stripe.py`** — separate router/prefix; doc collapses it into `routers/webhooks.py`.
- **`backend/tasks/section_generation.py`** — `run_section` lives here; doc lists only film/report/notifications task files.
- **`assemble_and_deliver` task** (3rd task in report_generation queue) — doc implies `generate_report` does the PDF/upload/notify work itself.
- **Section-cache short-circuit** in `_try_section_cache_hit` (`report_generation.py:110-155`) — on a single-film regeneration with cached sections 1-4 at the same `prompt_version`, the chord is skipped entirely. Not described.
- **Vertex AI / GCS dual-backend** is implemented end-to-end (`gemini.py:122-128`, `gemini_files.py:121-154`). Doc treats Vertex as future-only.
- **`films.synthesis_failed`** column (migration 004) — exists, never written.
- **`film_chunks.extraction_output` + `extraction_status`** (migration 016) — required for Prompt 0A storage; missing from doc's schema.
- **`film_analysis_cache.synthesis_document`** column (migration 010) — not in doc's cache schema.
- **`reports.context_cache_uri`** (migration 006) — column used to persist cache URI for cleanup.
- **`payments` (013)** and **`notifications` (012)** tables — referenced in code, not in doc's schema discussion.
- **Sentry / Datadog / PostHog** — listed in doc's OBSERVABILITY (932-934) and `requirements.txt:17-18`, but **never imported or initialized** anywhere. Env vars exist, never used.
- **Orphaned Gemini file cleanup task** (ARCHITECTURE.md:763-766) — described but not implemented.
- **Batch API routing + `report_generation_realtime/batch` queues** (ARCHITECTURE.md:1497-1503) — not implemented; only one report queue.
- **Subscription tiers** (STARTER/COACH/PROGRAM, ARCHITECTURE.md:1676-1694) — env vars reserved but no subscription code path; only per-report Stripe checkout.
- **`report_feedback` table** (ARCHITECTURE.md:1669) — does not exist in migrations.
- **`task_acks_late=True`, `worker_prefetch_multiplier=1`, `broker_transport_options.visibility_timeout=10800`** (`celery_app.py:27-32`) — important reliability tunings, undocumented.
- **5-minute Gemini HTTP timeout** (`services/ai/gemini.py:75-78`) — load-bearing bugfix.
- **`reports.status = 'partial'`** — real state for some-sections-errored reports (`report_generation.py:1079`); doc mentions partial reports conceptually but not as a status value.
- **CI/CD hygiene (PR audit)** — workflows, gitleaks, Dependabot, branch protection, ruff/mypy/eslint/prettier, PR template, README — none mentioned (arguably ops, not architecture, but worth at least a pointer).

**Recommended action:** Significant rewrite — concentrated on the report pipeline (688-731), intelligence map (1141-1200), cost math (1422-1469), AI provider abstraction (1020-1138), and the backend layout tree (72-108).

---

## SCHEMA.md

**Status:** Mostly current

**What's accurate:**
- All 14 user-facing tables (`users`, `teams`, `roster_players`, `films`, `film_chunks`, `reports`, `report_films`, `report_sections`, `corrections`, `film_analysis_cache`, `dead_letter_tasks`, `notifications`, `payments`, `fallback_events`) exist in the correct migration numbers (001-014).
- `users` (001): every column, type, default, `UNIQUE (clerk_id)`, both indexes (`idx_users_clerk_id`, partial `idx_users_stripe_customer_id`) match.
- `teams` (002): columns, default `level = 'unknown'`, `idx_teams_user_id` match.
- `roster_players` (003): columns, `UNIQUE (team_id, jersey_number)`, both indexes match.
- `films` (004): all columns including `synthesis_failed boolean NOT NULL DEFAULT false`, four indexes (`idx_films_user_id`, `idx_films_team_id`, partial `idx_films_status`, partial `idx_films_file_hash`).
- `film_chunks` (005): original columns, `UNIQUE (film_id, chunk_index)`, both indexes.
- `reports` (006): all columns including `report_type` and `context_cache_uri`, three indexes match.
- `report_films` (007): composite PK, `idx_report_films_film_id`.
- `report_sections` (008): all columns, `UNIQUE (report_id, section_type)`, both indexes.
- `corrections` (009): all columns (no `deleted_at`), all six indexes.
- `film_analysis_cache` (010): all columns including nullable `synthesis_document text`.
- `dead_letter_tasks` (011): all columns, all four indexes, no FK constraints (matches doc rationale).
- `notifications` (012): columns + both indexes (partial unread index).
- `payments` (013): all columns + two indexes.
- `fallback_events` (014): all columns + two indexes.
- `pgvector` extension at migration 015 (SCHEMA.md:671-672).
- `schema_migrations` housekeeping table created by `scripts/migrate.py:32-38` matches SCHEMA.md:657-661.

**What's stale:**
- **Migration list ends at 015** (`SCHEMA.md:42`). Missing entry: `016_add_film_chunks_extraction.sql`.
- **`film_chunks` CREATE TABLE block** (SCHEMA.md:213-225) does not list the migration-016 additions: `extraction_output text` and `extraction_status text NOT NULL DEFAULT 'pending'` (`migrations/016_add_film_chunks_extraction.sql:9-11`).
- **`film_chunks` index list** (SCHEMA.md:227-230) omits `idx_film_chunks_extraction_status ON film_chunks(film_id, extraction_status)` from migration 016.
- **`gemini_file_state` enum** (SCHEMA.md:220-221) is documented as `'uploading' | 'active' | 'failed'`. Code at `tasks/report_generation.py:934` writes a fourth value `'deleted'` after R2 chunk cleanup. Needs human verification — is the code right (add to doc) or wrong (use existing state)?

**What's missing:**
- **Migration 016** entirely (the two columns + the index above).
- **`gemini_file_state = 'deleted'`** sentinel.
- **Placeholder convention** — `run_chunk_synthesis` inserts `'{}'::jsonb` into `film_analysis_cache.sections` because the column is `NOT NULL` (`film_processing.py:887-895`); fills later. Worth a clarity note.
- **`fallback_events` table is unused.** Schema agrees with doc, but `INSERT INTO fallback_events` does not appear anywhere in `backend/`. Drift in the *other* direction — code hasn't implemented the writes the table was created for. Flag for human verification, not a doc edit.

**Recommended action:** Minor edit.

---

## FLOWS.md

**Status:** Significantly drifted

**What's accurate:**
- Sign-in / sign-up routes use Clerk-hosted components (`frontend/app/(auth)/sign-in/[[...sign-in]]/page.tsx`, `sign-up/...`).
- Auth gate via `clerkMiddleware` in `middleware.ts:1-16` with `/sign-in(.*)` and `/sign-up(.*)` as the only public routes.
- `/dashboard` empty-state onboarding (three numbered steps, "Create Your First Team" CTA, modal — `dashboard/page.tsx:131-167`).
- New Team modal — name field (max 100), level dropdown, Cancel/Create, posts `POST /teams` (`dashboard/page.tsx:77-94, 292-345`).
- Team page tabs (Roster / Films / Reports), Edit/Delete/Back header (`teams/[id]/page.tsx`).
- Roster delete confirmation copy: `"Remove #{jersey} {name}?"` matches FLOWS line 151.
- Team delete confirmation copy: `"Delete {team_name}? This cannot be undone."` matches FLOWS line 142.
- Film upload — drag/drop, file size shown, progress bar, three-step flow (initiate → R2 PUT → complete) at `upload/page.tsx`.
- Upload abort on failure calls `filmUploadAbort` (matches FLOWS line 223-224).
- Payment gate fires before generation (`reports.py:34-138`); frontend calls `createCheckoutSession` for paid path.
- Free first-report path via `consume_entitlement(path='free')` decrements `reports_used`.
- Report status page polls (cadence drifted — see below), shows status badge, error_message, presigned PDF link, six-section progress tracker in canonical order.
- Notifications: backend returns 50 newest; frontend renders unread inline with View/Dismiss; `markNotificationRead` wired.
- Admin gate is per-request: `Depends(require_admin)` on every admin route; frontend `admin/layout.tsx:21-31` probes on mount.
- Admin Patterns page — version filter, by-category / by-section tables with error-rate coloring.
- Admin Users page — table with email, reports, credits, joined; "Add Credits" → number input → grant.

**What's stale:**
- **Route map** (FLOWS:22-37):
  - `/teams` listed as a route — **does not exist** (`frontend/app/teams/` has no `page.tsx`).
  - `/admin/corrections` listed — corrections actually live at **`/admin`** itself (`frontend/app/admin/page.tsx`); the admin nav even labels `/admin` as "Corrections" (`admin/layout.tsx:58-60`).
  - `/admin/dead-letters` listed (lines 36, 369-372) — **does not exist**; no replay/dismiss endpoint either.
- **Competition level dropdown** (FLOWS:120) — code has `EYBL Scholastic` in addition to doc's list (`dashboard/page.tsx:17-26`). Team-page edit dropdown is internally inconsistent — missing `eybl_scholastic` (`teams/[id]/page.tsx:278`).
- **Add/Edit player fields** (FLOWS:159-165) — doc lists Jersey + Name + Position dropdown + Height + Dominant-hand dropdown + Role dropdown + Notes. UI only exposes Jersey + Name + Position-as-free-text (`teams/[id]/page.tsx:426-433`). Backend schema carries all the fields; UI form does not. No inline-on-click edit on rows.
- **Roster empty-state copy** (FLOWS:154) — doc says `"...attribute plays to specific players."`; code says `"...identify players in the film."`.
- **Roster empty-state CTA** (FLOWS:155) — doc says "Add First Player"; code says "Add Player" always.
- **Film card actions** (FLOWS:182) — doc says completed film shows per-card "Generate Report"; code shows one bottom-of-tab button (`teams/[id]/page.tsx:551-559`). No per-film generate, no delete, just Retry on error rows.
- **Film delete** (FLOWS:184) — doc says confirmation modal + soft delete; **no UI exists, no backend DELETE endpoint exists**.
- **Films empty state** (FLOWS:178) — doc copy `"No film uploaded yet."`; code `"No films uploaded yet for this team."`.
- **Reports empty state** (FLOWS:194) — doc copy and condition both wrong (code only shows it when no processed films exist; `teams/[id]/page.tsx:546-550`).
- **Upload accepted formats** (FLOWS:205) — doc `MP4, MOV, MKV, AVI`; code `MP4, MOV, AVI, WebM` (`upload/page.tsx:24-28, 134`). MKV removed, WebM added.
- **Upload max size 10GB** (FLOWS:206) — UI does not display or enforce a max; backend `routers/films.py` does not check `file_size_bytes` either.
- **Upload progress UI** (FLOWS:214-218) — doc says percentage + ETA + Cancel button; code shows percentage only (no ETA, no cancel).
- **Upload retry** (FLOWS:222-224) — doc says retry failed part up to 3x silently; code does a single `XMLHttpRequest` PUT with no retry (`upload/page.tsx:55-73`).
- **Upload polling** (FLOWS:230, 235) — doc says upload page polls `GET /films/[id]` every 10s; code does no polling on upload page — shows static "Go to Dashboard" link after `step==='done'`. Polling lives on the team page instead (`teams/[id]/page.tsx:131-153`).
- **Dashboard in-progress report banner** (FLOWS:99-105) — described in doc; **does not exist** in code. Dashboard doesn't poll reports.
- **Report status page polling cadence** (FLOWS:296, 312) — doc says every 5s; code polls every 10s (`reports/[id]/page.tsx:177`).
- **Report status page ETA copy** (FLOWS:295) — `"~12 minutes remaining"` not implemented; only `generation_time_seconds` shown after completion.
- **Report status "Try Again" button** (FLOWS:308) — does not exist; error state just shows the error.
- **Stripe redirect URLs** — doc says success `/reports/[id]?payment=success`, cancel `/teams/[id]`. Code (`stripe.py:129`) goes to `/dashboard?checkout=success|cancel`. Dashboard does not read those query params.
- **Stripe endpoint name** (FLOWS:274) — doc `POST /payments/checkout`; actual `POST /stripe/create-checkout-session` (`stripe.py:21`, `lib/api.ts:285`).
- **`POST /reports/[id]/download`** (FLOWS:301) — does not exist. `pdf_url` is embedded in the `getReport` response (`reports.py:232-243`).
- **In-app notifications display** (FLOWS:326-328) — doc describes nav-bar badge + dropdown; code renders inline banner-style list on dashboard. No nav bar exists.
- **Notifications query param `unread=true`** (FLOWS:331) — not supported; frontend filters client-side.
- **Admin home `/admin` summary stats** (FLOWS:340-341) — `/admin` is just the Corrections page; no stats home.
- **Admin corrections UX** (FLOWS:343-355) — doc says click claim → ✓/✗ → correct text; code is a manual form requiring you to type report_id, film_id, ai_claim, category, confidence, prompt_version, admin_notes (`admin/page.tsx:130-253`).
- **Admin Pattern Analyzer filters** (FLOWS:359, 361) — doc says date-range + Refresh; code has only a version selector and no Gemini recommendation text.
- **Admin User Management "last active"** (FLOWS:365) — not in code; backend doesn't return it.
- **Section 6 label** — FLOWS:293 calls it "In-Game Adjustments"; code renders "Adjustments & Practice Plan" (`reports/[id]/page.tsx:14`).

**What's missing:**
- **Dashboard "Recent Films" list** (last 5, status badges) — `dashboard/page.tsx:256-286`.
- **Dashboard error fallback** with Retry button + reachability/expired-session explanation — `dashboard/page.tsx:107-128`.
- **Film status set** — `uploaded`, `processing`/`chunks_uploaded`, `processed`, `error` (`teams/[id]/page.tsx:28-75`). Doc lists only four; `chunks_uploaded` and `uploaded` are intermediate states.
- **Report status `partial`** badge (yellow) on report page and team page (`reports/[id]/page.tsx:61-66`, `teams/[id]/page.tsx:531-540`).
- **Report status `pending`** badge before processing starts.
- **Per-section model_used + generation_time** under each completed section row (e.g., `gemini-2.5-pro · 42s`).
- **Retry Film button** on error rows; calls `POST /films/{film_id}/retry` (`films.py:154-179`).
- **`POST /dev/seed-user`** (replaces Clerk webhook in dev) — called by dashboard and admin layout in dev mode.
- **JWT refresh after long uploads** — `upload/page.tsx:75-79` fetches a fresh JWT before `upload-complete` because Clerk tokens expire in ~60s.
- **No-team-selected state on `/upload`** with Dashboard link.
- **`POST /notifications/read-all`** endpoint + API client function exist but no UI uses them.

**Recommended action:** Significant rewrite.

---

## PROMPTS.md

**Status:** Stale

**What's accurate:**
- All 8 prompt files on disk are documented in PROMPTS.md (chunk_extraction, chunk_synthesis, offensive_sets, defensive_schemes, pnr_coverage, player_pages, game_plan, adjustments_practice).
- Loader format (PROMPTS.md:17-30) — `VERSION:` header + `---` delimiter — matches `services/prompts.py:30-39` (modulo a tiny string-handling difference noted below).
- Sections 1-4 documented at v1.0 on disk and v1.0 in doc (PROMPTS.md:481-483, 550-553, 626-628, 708-710).
- Sections 5-6 documented at v1.0 on disk and v1.0 in doc (PROMPTS.md:768-770, 848-850).
- "Synthesis-only / Option 3" note (PROMPTS.md:166) accurately reflects that sections 1-4 receive the synthesis doc text, not video.
- Prompt-to-PDF mapping table (PROMPTS.md:988-995) matches disk file names.
- Prompt 0A + 0B are documented at all (PROMPTS.md section starting line 109).

**What's stale:**
- **Prompt 0A version markers** — PROMPTS.md:174, 177 say `VERSION: v1.5`; disk is **v1.6** (`backend/prompts/chunk_extraction.txt:1`).
- **Prompt 0B version markers** — PROMPTS.md:256, 259 say `VERSION: v1.5`; disk is **v1.6** (`backend/prompts/chunk_synthesis.txt:1`).
- **Footer** PROMPTS.md:467-468 — "Prompt 0 disk versions v1.5" / "Production Prompt 0 pair: chunk_extraction v1.5 + chunk_synthesis v1.5" — stale.
- **Changelog truncation (chunk_extraction)** — PROMPTS.md:178-180 shows only v1.5 + v1.0. Disk has v1.0, v1.1, v1.2, v1.3, v1.4, v1.5, v1.6 entries.
- **Changelog truncation (chunk_synthesis)** — PROMPTS.md:260-262 shows only v1.5 + v1.0. Disk has v1.0, v1.2, v1.3, v1.4, v1.5, v1.6.
- **Mirrored bodies** (PROMPTS.md:182-243 for Prompt 0A, PROMPTS.md:264-405 for Prompt 0B) are the v1.0 baseline. Doc flags this at line 174/256 but the mirror is now 6 revisions stale — readers may copy/paste old text. Missing rules include roster-spelling enforcement, Horns/5-out disambiguation, zone shell cues, transition count tightening, REACTIVE-VS-ZONE tagging, canonical geometry, two-layer defended PnR, OOB sweep, final-score reconciliation, defended-PnR confidence caps, OTD/separation standout definition, etc.
- **Footer summary** PROMPTS.md:1004 — "Current prompt versions: all sections at v1.0" — misleading. Sections 1-6 are v1.0, Prompt 0A/0B are v1.6.
- **Footer date** PROMPTS.md:1003 — "Last updated: Phase 0 — Context Engineering" — body has been touched many times since.
- **Loader snippet** (PROMPTS.md:19-26) is close-but-not-exact vs `services/prompts.py:30-41` (e.g., `lines[0].replace("VERSION: ", "")` with trailing space in doc; `first_line.replace("VERSION:", "")` no trailing space in code; `raw.split("---\n", 1)` in doc; `raw.split("\n---\n", 1)` in code). Minor behavioral difference (requires preceding newline in code).

**What's missing:**
- **Cache-key composition** `{sections_prompt_version}|{preprocess_prompt_version}` from `services/prompt_versions.py:8,41` is not formally documented in the PROMPT VERSIONING PROTOCOL section (only a passing mention at PROMPTS.md:164).
- **`+` join behavior** when chunk_extraction and chunk_synthesis versions diverge (`services/prompt_versions.py:38`: `f"{v0a}+{v0b}"`) — undocumented; current `v1.6|v1.6` happens to match.
- **`get_film_analysis_cache_prompt_version()`** function (canonical source) — referenced in CLAUDE.md, not in PROMPTS.md versioning protocol.
- **Sentinel behavior** of `offensive_sets.txt` — its version is the sentinel for the entire 6-section bundle in `prompt_versions.py:9-10`. Bumping `defensive_schemes.txt` alone would not invalidate the cache; this is operationally important and undocumented.
- **Missing changelog entries** for v1.1-v1.4 (extraction) and v1.2-v1.4 (synthesis).

**Recommended action:** Significant rewrite (concentrated on the Prompt 0 section + footers + versioning protocol).

---

## AGENTS.md

**Status:** Significantly drifted

**What's accurate:**
- Four queues and their assignments (`celery_app.py:35-40`).
- Task names registered match expected list (`process_film`, `extract_chunk`, `run_chunk_synthesis`, `generate_report`, `run_synthesis_sections`, `assemble_and_deliver`, `run_section`, `notify_coach`).
- `extract_chunk` timeouts soft 480s / hard 600s, `max_retries=3` (`film_processing.py:511-512`).
- `run_chunk_synthesis` timeouts soft 600s / hard 720s, `max_retries=2`, retry delay 60s (`film_processing.py:775-779`).
- `generate_report` timeouts soft 1500s / hard 1800s, `max_retries=3` (`report_generation.py:169-170`).
- `run_synthesis_sections` timeouts soft 600s / hard 720s, `max_retries=2` (`report_generation.py:716-720`).
- `assemble_and_deliver` timeouts soft 600s / hard 720s, `max_retries=2` (`report_generation.py:967-971`).
- `run_section` timeouts soft 480s / hard 600s, `max_retries=3` (`section_generation.py:82-85`).
- `notify_coach` timeouts soft 25s / hard 30s, `max_retries=3`, retry 5s (`notifications.py:57-60`).
- `acks_late=True` on every task; `celery_app.py:27`.
- Worker startup recovery implemented exactly as spec'd at `celery_app.py:46-113`.
- Atomic last-chunk detection via `pg_try_advisory_xact_lock` at `film_processing.py:662-678`.
- Rate-limit buckets `gemini-2.5-pro` (3/min), `gemini-2.5-flash` (15/min), `gemini-file-api` (10/min) in `services/rate_limit.py:7-11`.
- Dead-letter writes from every task's terminal-retry branch; schema matches.
- /tmp tracking with `film_id` prefix and `_cleanup_tmp` in `finally`.
- `get_valid_chunk_uris` re-uploads chunks <1h from expiry (`uri_expiry.py:33-37`).
- `run_synthesis_sections` deletes context cache in `finally` (`report_generation.py:858-880`).
- `_run_text_section` Flash → Claude fallback (`report_generation.py:530-651`).
- `run_section` idempotency check returns early on `complete` status.
- `assemble_and_deliver` ordering: chunks deleted only after `reports.status` written.
- PDF assembly with errored sections continues if `error_count < 6`.
- No-direct-provider-import rule honored (only `services/ai/router.py:11-13` imports providers).
- `acquire_gemini_slot` on every Gemini call, including `gemini-file-api` from `services/gemini_files.py:45`.

**What's stale:**
- **Task count** — AGENTS.md:12 says "9 Celery tasks"; OVERVIEW table at 17-26 lists 7; footer at 892 says "9 tasks defined". **Actual count is 8** (CLAUDE.md is correct).
- **`process_film` timeouts** — AGENTS.md:88, 124-125 says soft 3300s (55 min) / hard 3600s (60 min); code uses **7000s / 7200s** (~117 min / 120 min) at `film_processing.py:261-262`. Error message string at lines 452, 458 still says "55 minutes" — stale on both sides. The bump was likely driven by Docker FFmpeg being ~10x slower than native (per CLAUDE.md).
- **SoftTimeLimit message** AGENTS.md:187 — same "55 minutes" issue.
- **`process_film` numbered steps** (line 140-144) skip directly to step 14 on cache hit; code at `film_processing.py:325-342` just calls `_update_film_status("processed")` and returns. The numbered narrative is stale.
- **Sentry context** — AGENTS.md Rule 4 says every task sets Sentry context. `grep -rn "sentry" backend/` returns zero hits. Sentry SDK is in `requirements.txt:17` but never imported.
- **Synthesis auto-trigger** — AGENTS.md step 8 of `run_chunk_synthesis` (lines 330-344) says it auto-enqueues `generate_report`. **Not implemented** — `film_processing.py:899-908` just marks the film `processed` and logs.
- **Graceful synthesis degradation** — AGENTS.md:346-351 says final synthesis retry should set `status='processed'` + `synthesis_failed=true` and let sections 1-4 run without the synthesis document. Code at `film_processing.py:910-922` sets `status='error'` instead. The `films.synthesis_failed` column exists but is never written.
- **`notify_coach` parameter name** — doc uses `type=`; code uses `notification_type=` everywhere (call sites in `film_processing.py:247,362,476,493` and `report_generation.py:522,1051,1112`).
- **Partial-report notification message** — AGENTS.md:680-681 says `"Your report is ready with {n} of 6 sections complete. One or more sections could not be generated."`; `notifications.py:71` says `"Your report is ready with some sections incomplete."` (no `{n}` substitution).
- **Retry backoffs**:
  - `generate_report`: AGENTS.md:90 says `30s/120s/480s`; code uses `30 * (2**retries)` = 30/60/120s (`report_generation.py:435`).
  - `run_section`: doc says `30s/120s/480s`; code uses `30 * (2**retries)` = 30/60/120s (`section_generation.py:222`).
  - `assemble_and_deliver`: doc says `60s/180s`; code uses `60 * (3**retries)` = 60/180/540s (`report_generation.py:1159`) — off for retry #2.
- **`run_synthesis_sections` signature** — AGENTS.md:496 doesn't reflect that `chord_results` can be `None` (passed in the section-cache short-circuit at `report_generation.py:343`).
- **Synthesis-only mode** — AGENTS.md `generate_report` step 11 and `run_synthesis_sections` step 10 both describe "delete the Gemini context cache". In synthesis-only mode `create_context_cache` returns a `vertex:no-cache:<json>` sentinel; there is no real Google cache to delete. The cache-lifecycle narrative is architecturally stale.
- **Pseudocode at AGENTS.md:196** shows `notify_coach.delay(...)` outside the `if retries >= max_retries` guard; code (`film_processing.py:493`) only fires on final retry. Behavior is fine; pseudocode is misleading.

**What's missing:**
- **Section-cache short-circuit** (`_try_section_cache_hit`, `report_generation.py:110-155`) — entire optimization not described. On single-film regeneration at the same `prompt_version`, the chord is skipped, sections 1-4 marked `model_used = 'cached'`, and `run_synthesis_sections` is invoked directly with `cache_uri=""`.
- **`_cache_section_outputs` write loop** (`report_generation.py:654-704`) — closes the loop above; only indirectly mentioned at AGENTS.md:518-520.
- **`get_film_analysis_cache_prompt_version()` derivation** from prompt-file headers (per CLAUDE.md) — doc uses generic `{current_version}` placeholder.
- **`films.synthesis_failed`** column exists but is never written (related to graceful-degradation drift above).
- **`_fail_film_from_chunk` "first chunk to fail wins" atomicity** (`film_processing.py:223-247`) — conditional `WHERE id = %s AND status NOT IN ('error', 'processed')` so only the first failing chunk notifies the coach.
- **`extract_chunk` partial-state resume** (`film_processing.py:547-572`) — if chunk's Gemini file is `active` but Prompt 0A failed, the task reuses the URI rather than re-uploading.
- **`extract_chunk` rate-limit specificity** — AGENTS.md step 3 (line 240) just says "Acquire Gemini rate limit slot"; code specifically acquires `gemini-2.5-pro` for Prompt 0A (`film_processing.py:626`).
- **Gemini File API upload bucket** — `extract_chunk` upload also acquires `gemini-file-api` slot (`gemini_files.py:45`); not in AGENTS.md.
- **`broker_transport_options.visibility_timeout = 10800`** (3 hours) — `celery_app.py:30-32`.
- **`task_default_queue = "notifications"`** — `celery_app.py:41`.
- **`worker_prefetch_multiplier=1`** — `celery_app.py:28`.
- **`GEMINI_BACKEND=vertex` short-circuit** in `uri_expiry.py:25-27` (skips re-upload scan for GCS URIs).
- **`assemble_and_deliver` `error_count == 6` full-failure-with-credit path** (`report_generation.py:1041-1057`) — duplicates logic from `_handle_all_sections_errored`; doc presents them as identical.
- **5-min Gemini HTTP timeout override** (`services/ai/gemini.py:75-78`) — load-bearing.

**Recommended action:** Significant rewrite (concentrated on the timeout/retry tables, synthesis-only mode narrative, section-cache short-circuit, and the missing reliability tunings).

---

## EVALS.md

**Status:** Stale

**What's accurate:**
- **Phase 1 evals — feature existence**: auth/Clerk webhook/teams/roster routers exist; duplicate jersey 409 at `routers/roster.py:67-68` via UNIQUE constraint (`migrations/003_create_roster_players.sql:15`); film L1 browser MIME rejection at `upload/page.tsx:26`; L3 FFprobe duration limits at `services/ffprobe.py:112-122`.
- **Phase 2 infrastructure exists**: `extract_chunk` task (`film_processing.py:515`); URI re-upload (`services/uri_expiry.py:16-57`); context cache lifecycle (`gemini.py:114,197`, orchestrator at `report_generation.py:349`); parallel sections chord (`report_generation.py:386-394`).
- **Phase 3 evals (code present, eval pending)**: payment gate (`services/payment_gate.py`); Stripe checkout via `routers/stripe.py:21-157`; failure credit at `report_generation.py:477-486`; dead-letter writes in every task module; startup recovery at `celery_app.py:53-56`.
- **Phase 4 evals (code present, eval pending)**: admin gate per request via `require_admin` at `services/clerk.py:126-131` used in `routers/admin.py:57, 147, 217, 310, 350`; correction save preserves `ai_claim` + `prompt_version` (`admin.py:174-187`); pattern analyzer endpoint at `admin.py:214`; frontend admin pages exist.
- Notifications writes + list/mark-read implemented.
- All 8 prompt files exist at the referenced paths; Prompts 0A/0B at v1.6.
- Golden-set alignment — all 5 ground-truth folders exist (`ground_truth.md`, `metadata.md`, `film_watch_notes.md` per film).

**What's stale:**
- **Section-fallback eval** (EVALS.md:49) claims `fallback_events` row gets written on Claude fallback. Migration exists (`migrations/014_create_fallback_events.sql`) but **no code writes to it**. `_run_text_section` in `report_generation.py:578-599` swallows the Flash exception and calls Claude with no DB insert. Eval pass condition cannot be met by current code.
- **Film validation L2 eval** (EVALS.md:39) references `POST /films/upload-url`; real endpoint is `POST /films/upload-initiate` (`routers/films.py:38`). Worse, that endpoint performs **no MIME/extension validation** — only team-ownership check. The eval's pass condition (400 returned, no presigned URL) cannot currently be met.
- **`backend/evals/eval_log.csv`** (EVALS.md:329, 334) — directory and file do **not exist**.
- **`EVAL_SCORES.md`** (EVALS.md:330, 345) — file does **not exist** at repo root (also referenced by TRAINING.md, ROADMAP.md, golden_set/README.md). The internal grading UI that would auto-write it also doesn't exist.
- **Paid-second-report eval flow** (EVALS.md:53) reads as though calling "create report" returns a checkout URL inline. Real flow is two-step (`POST /reports` → `payment_required=True` → `POST /stripe/create-checkout-session`). Needs human verification on whether the eval description is operationally still meaningful as written.

**What's missing:**
- **Prompt 0A/0B golden-set methodology** — EVALS.md:114 uses a 1-5 rubric over 3 consecutive chunks; ROADMAP/CLAUDE.md describe the Stage 1 gate as golden-set captured/missed/hallucinated. Two scoring systems coexist without explicit reconciliation.
- **No eval for `film_analysis_cache` / preprocess version invalidation.** `services/prompt_versions.py` derives `prompt_version` from headers; CLAUDE.md flags that v1.6 prompts have not invalidated Neon rows. No eval question asks "does a prompt version bump cause cache re-run?"
- **No eval for Stripe webhook signature verification** (`routers/stripe.py` uses `verify_webhook`). Critical security control, untested.
- **No eval for Clerk Svix webhook signature verification** — same gap.
- **No eval for rate-limit token buckets** (`services/rate_limit.py`). Critical to unit economics + throughput.
- **No eval for the SDK timeout fix** (`http_options=types.HttpOptions(timeout=300_000)` in `services/ai/gemini.py::_get_dev_client()`). Recent fix (2026-05-13), no regression guard.
- **No eval for `film_chunks` cleanup** after `reports.status = complete` (CLAUDE.md product flow step 14).
- **No eval for chord callback degradation** — `run_synthesis_sections` (`report_generation.py:722-755`) distinguishes "all errored" vs "some succeeded" but no eval covers the partial path.
- **No eval for the internal grading UI itself.** TRAINING.md §4.5 calls it the bottleneck-breaker; EVALS.md never asks "does the grading UI write `EVAL_SCORES.md` correctly?" — and it can't, because neither exists yet.

**Recommended action:** Significant rewrite — fix stale infrastructure-eval rows (L2 endpoint, `fallback_events` claim), mark missing eval-log files as pending or seed them, then add the missing eval questions for cache invalidation, webhook signatures, rate limits, and the SDK timeout regression guard.

---

## COSTS.md

**Status:** Significantly drifted

**What's accurate:**
- **Model identifiers**:
  - Gemini 2.5 Pro for sections 1-4 — `GEMINI_PRO_MODEL = "gemini-2.5-pro"` (`gemini.py:37`); used in `run_section` (`section_generation.py:138, 161`).
  - Gemini 2.5 Flash for sections 5-6 — `GEMINI_FLASH_MODEL = "gemini-2.5-flash"` (`gemini.py:38`); `_run_text_section` calls `analyze_text` (`report_generation.py:565, 567`).
  - Claude 3.5 Sonnet fallback — `CLAUDE_SONNET_MODEL = "claude-3-5-sonnet-20241022"` (`anthropic.py:22`); fallback at `report_generation.py:578-599`.
- **Prompt 0A uses Gemini 2.5 Pro** (`film_processing.py:626-632`).
- **Prompt 0B uses Gemini 2.5 Flash** (`film_processing.py:864-870`).
- **Payment gating** — first-report-free + credits skip Stripe (`services/payment_gate.py:46-50`).
- **Failure credit** path (`report_generation.py:476-496`).
- **Two R2 buckets** (films + reports) per `.env.example:25-26`; used in `film_processing.py:271`, `report_generation.py:1069`.
- **1.8GB compression threshold** (`film_processing.py:369`).
- **STARTER tier** is the only configured/used Stripe price — `STRIPE_REPORT_PRICE_ID` at `routers/stripe.py:36-38`.

**What's stale:**
- **CRITICAL — Gemini context caching is NO LONGER USED.** COSTS.md §"Sections 1-4 — Gemini 2.5 Pro with Context Caching" (lines 111-138) is the financial cornerstone ("This is what makes the unit economics viable", line 149). Code has explicitly disabled Google's context cache:
  - `services/ai/gemini.py:7-23` — docstring: *"SYNTHESIS-ONLY MODE (Option 3): Sections 1-4 no longer re-read the video... `create_context_cache()` no longer calls Google's cache API."*
  - `services/ai/gemini.py:50` — `NO_CACHE_PREFIX = "vertex:no-cache:"` sentinel.
  - `services/ai/gemini.py:130-159` — `_create_context_cache_dev` returns the sentinel.
  - `services/ai/gemini.py:242-250` — sections 1-4 run with `[text_context, prompt]` text Parts only.
  - **Cost impact: massive.** $4.75 cache-creation + $1.41 cache-reads + $2.13 cache-storage = $8.29 of the $8.39 sections-1-4 figure is computed on video tokens that are no longer sent.
- **Token math baseline** (lines 116-119, 122, 142-146) — assumes video tokens at section-call time. Video tokens are only billed once during Prompt 0A.
- **"Cache storage: 1.89M tokens stored for 15 minutes ... $2.13"** (line 128) — zero in reality.
- **"Sections 1-4 run in parallel reading from shared cache"** (line 113) — parallel is true, but the "cache" is a JSON sentinel with text context. Section 1 no longer "pays full price to create the cache" while 2-4 "pay 10%" — all four pay the same text-only rate.
- **"Without context caching: $19.02"** (line 146) — also stale; the counterfactual path is unreachable.
- **Doc footer "Last updated: Phase 0 — Context Engineering"** (line 518) — predates Prompts 0A/0B (Phase 2, 2026-04-20) and the synthesis-only refactor.
- **`film_analysis_cache.sections` application-level cache short-circuit** (`report_generation.py:288-344`) — sections 1-4 cost **$0** with `model_used = 'cached'` on a hit. COSTS.md models cache hits as Prompt-0-only skip (lines 226-228) and never models the section-cache short-circuit.

**What's missing:**
- **Prompt 0A / Prompt 0B preprocess stage is absent entirely.** Doc was last touched in Phase 0; Prompts 0A/0B were added Phase 2 (CLAUDE.md "Phase 2: File flow + Prompt 0A/0B wiring complete (2026-04-20)").
  - Prompt 0A: `extract_chunk` task, one Gemini 2.5 Pro call per chunk on chunk video (`film_processing.py:610-654`). ~4-5 chunks per 2-hour film.
  - Prompt 0B: `run_chunk_synthesis` task, one Gemini 2.5 Flash text call concatenating all chunk extractions (`film_processing.py:864-870`).
  - Paid once per `file_hash`, cached by `prompt_version` (`film_processing.py:339-342`).
- **Synthesis-only architecture cost re-baseline.** With Google cache disabled, the doc's per-report numbers (sections 1-4 = $8.39, total = $13.83) need a full recompute. The new dominant variable cost is video input at Prompt 0A (5 × 395K ≈ 1.97M tokens × $2.50/M ≈ $4.93), then sections 1-4 each consume the synthesis doc (~6K tokens) + roster (~500 tokens) at standard rate.
- **Application-level section-cache layer** (`film_analysis_cache.sections`) — second cache type, reuses full sections 1-4 outputs across reports at same `(file_hash, prompt_version)`. Not modeled.
- **Compression cost / failure mode** — COSTS.md:190 assumes "compressed to ~1.5GB" with no compute-cost line. Empirical 40-min FFmpeg cost on real Film 04 noted in CLAUDE.md is not reflected in the $0.096 film-worker estimate at line 184.
- **Coach + Program tier prices reserved but unused.** `STRIPE_COACH_PRICE_ID` and `STRIPE_PROGRAM_PRICE_ID` exist in `.env.example:36-37` but are not referenced anywhere in code. Doc presents COACH and PROGRAM tier economics (lines 308-368) as concrete; no subscription-mode Stripe flow yet — only one-off `mode="payment"` at `routers/stripe.py:128`.
- **Batch API path** (COSTS.md:252-278) — entirely unimplemented. No `batch` references in `backend/`. Blended margins depending on "40% batch routing" are theoretical only.
- **Rate-limit buckets** (`services/rate_limit.py:7-11`) — not modeled in compute time estimates (lines 183-185).
- **Vertex backend path** (`GEMINI_BACKEND=vertex`) exists in code (`gemini.py:103-109`); pricing can differ from Developer API; doc only models Developer API rates.

**Recommended action:** Major restructure — three independent architectural shifts (Google cache disabled, Prompts 0A/0B added, application-level section cache) have invalidated the central cost model. Every margin number in this doc is currently unreliable.

---

## Summary

- **Total docs reviewed:** 8
- **Current:** 0
- **Mostly current:** 1 (SCHEMA.md)
- **Stale:** 2 (PROMPTS.md, EVALS.md)
- **Significantly drifted:** 5 (STACK.md, ARCHITECTURE.md, FLOWS.md, AGENTS.md, COSTS.md)
- **Estimated work to refresh all docs:** **Large.** Five docs need significant rewrites and one (COSTS.md) needs a major recompute from scratch. The architectural shift to synthesis-only mode plus the addition of Prompts 0A/0B has invalidated load-bearing sections in ARCHITECTURE.md, AGENTS.md, and COSTS.md. The five-PR hygiene audit added an entire infra layer that no canonical doc currently acknowledges.

**Recommended update order:**

1. **SCHEMA.md** first — small, targeted edit (migration 016 + a couple of enum/index notes). Cheap to do, and it's load-bearing for AGENTS.md / ARCHITECTURE.md / EVALS.md which reference schema details.
2. **PROMPTS.md** — version-marker bumps (v1.5 → v1.6) + decide mirror-policy (full re-mirror vs. pointer + summary). Independent of the bigger architectural rewrites. Operationally important because the cache-key derivation lives here.
3. **ARCHITECTURE.md** — must come before AGENTS.md and COSTS.md because both depend on the synthesis-only pipeline being canonically described. Concentrate the rewrite on the report pipeline (688-731), intelligence map (1141-1200), and cost block (1422-1469). Also update the backend tree (72-108) and AI router (1020-1138).
4. **AGENTS.md** — once ARCHITECTURE.md establishes the synthesis-only narrative, reconcile the task tables (timeouts, retry backoffs, task count), document the section-cache short-circuit, and decide the graceful-degradation question.
5. **COSTS.md** — major restructure once ARCHITECTURE.md + AGENTS.md are aligned. Recompute all three pricing tiers against synthesis-only with Prompt 0A/0B baked in as the dominant variable cost line. Needs a working session with Tommy, not just an edit pass.
6. **STACK.md** — significant rewrite to add the hygiene-audit layer (CI, gitleaks, Dependabot, ruff/mypy/eslint/prettier, pre-commit, PR template, branch protection), correct the Gemini SDK references, fix the migration list and port remap. Independent of the pipeline rewrites; can run in parallel with #3-#5.
7. **FLOWS.md** — significant rewrite. Independent of backend pipeline docs; could be done in parallel. Many UI claims need updating and the admin section needs the most work.
8. **EVALS.md** last — once the upstream docs are accurate, then update the eval rubrics. Several missing eval questions (cache invalidation, webhook signatures, rate limits, SDK timeout regression) depend on other docs settling first.

**Cross-cutting threads to keep consistent across rewrites:**
- Synthesis-only mode (Option 3) — touched by ARCHITECTURE, AGENTS, COSTS, PROMPTS.
- Prompts 0A/0B pipeline — touched by ARCHITECTURE, AGENTS, COSTS, PROMPTS, EVALS, SCHEMA (migration 016 columns).
- Application-level section cache short-circuit — touched by ARCHITECTURE, AGENTS, COSTS.
- 5-PR hygiene audit — touched by STACK (heavily), arguably ARCHITECTURE/AGENTS (the CI workflows verify what those docs prescribe).
- `fallback_events` table created-but-never-written — drift in two directions (ARCHITECTURE asserts writes happen; EVALS depends on the row appearing; code does neither). Needs a "implement or remove" decision before either doc is updated.
