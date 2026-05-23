# DECISIONS.md — TEX v2

Architectural decisions log. Every significant decision made for TEX v2, why it was made,
what alternatives were considered and rejected, and what would cause the decision to be revisited.
Read this before proposing any architectural change. If a decision is documented here, it was
deliberate. Challenge it with evidence, not preference.

New decisions go at the bottom. Never modify a decision already logged — add a SUPERSEDED entry
that references the original and documents what changed and why.

---

## D-001 — Python 3.12 for backend and workers

**Decision:** All backend services (FastAPI API + all Celery workers) run Python 3.12.
Same version everywhere. No mixing.

**Rationale:** Python 3.12 has meaningfully improved error messages over 3.11 — stack traces
are more readable and debugging production failures is faster. Minor performance improvements
in the interpreter are real but not the primary reason. The primary reason is uniformity:
one Python version means one set of dependency constraints, one Dockerfile base image, and no
subtle compatibility bugs between services that share code (the workers import from the same
`services/` directory as the API).

**Alternatives considered:**
- Python 3.11: stable and widely used. Rejected because 3.12 improvements are real and the
  migration cost from 3.11 to 3.12 later is not zero.
- Python 3.13: not yet stable enough at time of decision. Revisit when 3.13 reaches broad
  library support.

**Reversal condition:** A critical dependency that TEX requires does not support 3.12.
In that case, evaluate whether the dependency can be replaced before downgrading Python.

---

## D-002 — FastAPI over Flask / Django

**Decision:** FastAPI is the web framework for the backend API.

**Rationale:** FastAPI provides async request handling, automatic OpenAPI schema generation
from Pydantic models, and native dependency injection — all of which matter for this codebase.
Async handling means the API does not block while waiting on DB calls or enqueuing tasks.
Pydantic integration means request validation is not a separate layer — it is the function
signature. Django's ORM, admin UI, and template system are all things TEX does not use;
Django's overhead is pure cost with no benefit here. Flask is synchronous by default and lacks
Pydantic integration natively.

**Alternatives considered:**
- Django: ruled out. ORM conflicts with the raw SQL requirement. Admin UI is unused.
- Flask: ruled out. Synchronous, no Pydantic integration, more boilerplate for validation.

**Reversal condition:** None anticipated. FastAPI is the correct tool for this workload.

---

## D-003 — Neon PostgreSQL over Supabase

**Decision:** Neon PostgreSQL is the database. Supabase is not used in v2.

**Rationale:** v1 ran on Supabase. Supabase's PgBouncer connection pooler in transaction mode
closed idle connections after ~10 minutes. Celery tasks that held a connection across long
processing windows hit this and failed mid-task with "connection terminated unexpectedly."
The v2 architecture eliminates this structurally — every DB call opens, executes, and closes.
No connection is held across a task boundary. Neon's PostgreSQL wire protocol behavior under
this pattern is predictable and correct. Additionally, v2 does not use Supabase Auth (Clerk
handles auth), Supabase Storage (R2 handles storage), or Supabase Realtime — three of the four
reasons to choose Supabase over raw Postgres. The fourth, the managed Postgres itself, Neon
does equally well with better branching support for schema migrations.

**Alternatives considered:**
- Supabase with structural fix: the connection bug would be fixed by the open/execute/close
  pattern regardless of which managed Postgres is used. Supabase was rejected anyway because
  the RLS policies from v1 reference `auth.uid()` — a Supabase-specific function that does
  not exist in raw Postgres. Porting those policies to Neon requires rewriting them, at which
  point the question is whether RLS is worth maintaining at all (see D-006).
- PlanetScale: MySQL, not Postgres. pgvector requires Postgres. Rejected.
- Self-hosted Postgres on Cloud Run: more operational complexity than Neon with no benefit at
  current scale.

**Reversal condition:** Neon's connection limits become a bottleneck at high concurrent report
volume. At that point, evaluate PgBouncer in front of Neon or migrate to Cloud SQL.

---

## D-004 — Raw SQL, No ORM

**Decision:** All database access uses raw SQL with psycopg2. No ORM. No SQLAlchemy.
No query builder. No Alembic.

**Rationale:** The schema is 15 tables, known in advance, and stable. ORMs pay off when
the schema is large, frequently changing, or when developers unfamiliar with SQL need to
interact with the database. None of these conditions apply to TEX v2. Raw SQL is explicit —
every query is visible, pasteable into Neon's console, and debuggable in isolation. ORM-generated
queries are invisible until something goes wrong, at which point you are debugging the ORM's
behavior as much as the query. Parameterized raw SQL also makes the mandatory `WHERE user_id = %s`
pattern structurally enforced — you cannot forget to add it because it is a function parameter.

**Alternatives considered:**
- SQLAlchemy Core (not ORM): still adds a query builder abstraction over SQL. Rejected for
  the same reason — the abstraction adds complexity without benefit at this schema size.
- SQLAlchemy ORM: rejected. Conflicts with the fresh-connection-per-call pattern and adds
  the most complexity for the least benefit.
- Tortoise ORM: async-native but the same objection applies.

**Reversal condition:** Schema grows beyond 30 tables with complex join patterns that become
difficult to maintain in raw SQL. At that point, evaluate SQLAlchemy Core (not ORM) for
query building while keeping raw connection management.

---

## D-005 — Cloudflare R2 over AWS S3

**Decision:** Cloudflare R2 is the object storage layer for both buckets (films and reports).

**Rationale:** R2 has no egress fees — data transferred out of R2 to the internet is free.
S3 charges $0.09/GB egress. A 2-hour film compressed to 1.5GB downloaded by a worker from S3
costs $0.135 per download. Workers download films multiple times (original download for
processing, potential re-downloads for re-upload). At volume this is material. R2 eliminates
this cost entirely. R2 uses the S3-compatible API, so the boto3 client works with a single
endpoint URL change. Migration cost to S3 is one environment variable change.

**Alternatives considered:**
- AWS S3: identical feature set, higher egress cost. Rejected solely on cost.
- Google Cloud Storage: would eliminate cross-cloud latency for workers on Cloud Run.
  Rejected because R2's zero-egress advantage outweighs the latency benefit at current
  film sizes, and GCS egress to Cloud Run within the same region is not free.
- Backblaze B2: also zero-egress to Cloudflare network. Fewer features, less mature SDK.
  Rejected in favor of R2's maturity.

**Reversal condition:** Gemini migrates to Vertex AI (see D-011). At that point, workers
upload chunks to GCS instead of Gemini File API. If all workers and storage move to GCP,
GCS becomes the natural choice and R2's egress advantage diminishes relative to GCS-to-CloudRun
zero-cost transfers within GCP. Reassess when Vertex AI migration occurs.

---

## D-006 — No Database-Level RLS

**Decision:** Neon has no Row Level Security policies. Data isolation is enforced entirely
at the application layer via mandatory `WHERE user_id = %s` on every user-facing query.

**Rationale:** TEX v2 has exactly one path to the database: FastAPI. Coaches do not connect
to Neon directly. There is no client SDK, no exposed GraphQL layer, no direct database access
from the browser. FastAPI verifies the Clerk JWT, extracts `user_id`, and enforces scoping
before any query runs. Database-level RLS on this architecture is a second lock on a door
that already has a guard. At scale with fresh connections per call and high poll frequency,
the mandatory `SET LOCAL` session variable that RLS requires adds measurable overhead with
zero security benefit given the architecture.

The one exception: the `corrections` table has a database-level write restriction. Only the
service role key can insert. This is enforced at the Neon level because the corrections table
is the proprietary training dataset and no coach account should ever touch it under any
circumstance — not through a bug, not through a misconfiguration, not through a missing
`WHERE` clause. The asymmetry (no RLS on user tables, hard DB restriction on corrections)
is intentional.

**Alternatives considered:**
- Full RLS on all tables: rejected because `auth.uid()` is a Supabase function that does not
  exist in raw Postgres. Porting the v1 RLS policies requires rewriting them, at which point
  the question is whether they provide any security benefit the application layer doesn't
  already provide. Answer: no, given the single-path architecture.
- Partial RLS (only on most sensitive tables): rejected for consistency. One enforcement
  mechanism is easier to audit than two.

**Reversal condition:** A second database access path is added — a public API, a webhook
that writes directly without going through FastAPI, or a third-party integration with
direct DB access. At that point, RLS becomes necessary.

---

## D-007 — Celery + Redis over alternatives

**Decision:** Celery 5 with Redis as broker and result backend for all async task processing.

**Rationale:** Celery's chord primitive is the correct implementation for the parallel section
generation pattern — fire 4 tasks simultaneously, execute a callback when all 4 complete.
This is not easily replicated with simpler queue systems. Celery also provides per-queue
concurrency controls, soft and hard timeouts, retry with exponential backoff, and task state
tracking — all of which TEX v2 uses. Redis as broker is the standard Celery broker for
production workloads and integrates with the token bucket rate limiter already in the design.

**Alternatives considered:**
- Cloud Tasks (GCP): managed, serverless, no Redis dependency. Rejected because Cloud Tasks
  does not have a native chord/group primitive. Implementing parallel section generation with
  a callback requires either polling or a custom fan-out mechanism — more complexity than
  Celery's built-in primitive.
- RQ (Redis Queue): simpler than Celery, Redis-native. Rejected because RQ has no equivalent
  to Celery's chord for parallel fan-out with callback.
- Dramatiq: similar to Celery, cleaner API. Rejected because Celery has a larger ecosystem,
  better documentation, and the chord primitive is more mature.

**Reversal condition:** Cloud Run's maximum request timeout (3600 seconds) and Celery's
operational complexity become a bottleneck at high scale. At that point, evaluate Cloud Tasks
with a custom chord implementation or a managed workflow service (Cloud Workflows).

---

## D-008 — 4 Separate Celery Queues

**Decision:** Four queues: `film_processing`, `report_generation`, `section_generation`,
`notifications`. Each runs on a separate Cloud Run service with independent scaling.

**Rationale:** Backpressure isolation. A 2-hour film being processed takes up to 60 minutes.
If film processing and notifications share a queue, a backlog of film jobs blocks coaches from
receiving notifications about completed reports. Separate queues mean separate worker pools.
Backpressure in one queue does not propagate to others. Independent scaling means section
workers (which need to scale to 10 during report generation peaks) do not consume resources
allocated to film processing workers (which run at concurrency=1 and need 8GB /tmp).

**Reversal condition:** Queue count increases complexity without meaningful isolation benefit.
If TEX's traffic pattern is consistently one queue at 0% and another at 100%, consolidation
may be correct. Monitor queue depths in Datadog before consolidating.

---

## D-009 — Dead Letter Queue in Neon, Not Redis

**Decision:** Failed tasks that exhaust all retries write to the `dead_letter_tasks` table
in Neon. No Redis dead letter queue.

**Rationale:** Redis is configured with AOF persistence but is still fundamentally a cache.
A Redis dead letter queue loses data if Redis is replaced, the AOF is corrupted, or the
instance is provisioned fresh. Neon is durable by design — it is the source of truth for all
application state. A failed task that disappears from a Redis dead letter queue on Redis
restart is a coach job that vanishes without a trace. A failed task in Neon is queryable,
replayable by UUID, and visible in the admin UI without any Redis access. The `task_args`
JSONB column stores the full original arguments, enabling replay with one function call.

**Alternatives considered:**
- Redis dead letter with AOF: rejected because AOF protects against clean restarts, not
  against Redis instance replacement or corruption.
- SQS dead letter queue: adds an AWS dependency to what is otherwise a GCP + Cloudflare stack.
  Rejected.

**Reversal condition:** None. The DB is always the correct location for durable failure state.

---

## D-010 — Film Fingerprint Cache (SHA-256)

**Decision:** Every film is hashed on download (SHA-256 of raw bytes). Before running any
Gemini analysis, the worker checks `film_analysis_cache` for a matching hash + prompt version.
A cache hit skips all LLM calls for sections 1-4.

**Rationale:** Multiple coaches regularly scout the same opponents — especially at EYBL events.
The first coach to upload a given film pays full Gemini cost. Every subsequent coach who uploads
the same film gets an instant result at zero Gemini cost. The cache hit rate compounds with
coach volume — at 500 coaches, popular EYBL programs are effectively analyzed once. The moat
argument: competitors who launch later and pay full API price on every report cannot match TEX's
unit economics at scale without building an equivalent cache, which requires an equivalent
coaching network to populate it.

Cache invalidation is by prompt version — a cache entry is stale when the prompt that generated
it has been superseded. This ensures coaches always receive analysis from the current prompt
quality, not a cached result from an older (potentially worse) prompt.

**Alternatives considered:**
- No caching — pay Gemini on every report: viable at launch with 10 coaches, unviable at 500.
  The decision to build the cache at Phase 0 means the compounding benefit starts from day one.
- Cache by film metadata (filename + size) instead of hash: rejected. Two films with the same
  filename and size can have different content. Hash is the only reliable identity.
- Perceptual hashing (for visually similar but not identical files): rejected. Too complex,
  too many false positives, and the signal is unreliable for game film where slight encoding
  differences are common. SHA-256 of raw bytes is exact and fast.

**Reversal condition:** SHA-256 computation on large files (4-8GB pre-compression) adds
meaningful latency to film processing. At that point, evaluate streaming hash computation
during the R2 download rather than hashing the complete file in memory.

---

## D-011 — Gemini Developer API Now, Vertex AI Later

**Decision:** TEX v2 launches on the Gemini Developer API. Migration to Vertex AI happens
when monthly Gemini spend justifies committed use discounts or when operational reasons favor it.

**Rationale:** The Developer API is simpler to set up and iterate on during Phase 0-3. No GCP
project configuration, no service account IAM setup for Vertex, no GCS bucket for file uploads.
The AI provider abstraction layer (router.py) and the GEMINI_BACKEND env var mean this migration
is one configuration change — no code changes to any file outside gemini.py. The operational
complexity of Vertex AI is real; pay it when the pricing benefit justifies it.

Vertex AI triggers:
1. Monthly Gemini spend exceeds the threshold where committed use discounts on Vertex AI
   produce material savings (estimate: >$2,000/month Gemini spend).
2. Gemini File API 48-hour expiry creates operational load that GCS's permanent storage would
   eliminate (the expiry check and re-upload logic becomes a no-op with GCS).

**Alternatives considered:**
- Launch on Vertex AI from day one: rejected. Operational setup complexity and IAM configuration
  slow down Phase 1-3 without any benefit at low volume. The abstraction layer means this
  decision does not need to be made at launch.

**Reversal condition:** Not applicable — this is a migration path, not a binary choice.

---

## D-012 — Prompt 0 Two-Stage Architecture (Extract Then Synthesize)

**Decision:** Film chunk analysis runs in two stages: a parallel per-chunk extraction pass
(Prompt 0A) followed by a single synthesis pass (Prompt 0B). Not a single combined prompt.

**Rationale:** Perception and reasoning are different cognitive tasks. Asking one prompt to
simultaneously watch video, count occurrences, identify players, reconcile vocabulary across
chunks, identify scheme changes, and produce a structured synthesis produces lower accuracy
on all of those tasks than separating them. The extraction pass asks Gemini to watch and log —
a perception task with a structured output format. The synthesis pass asks Gemini to reconcile
and reason across text inputs — a reasoning task with no video. Separation also enables
parallelism: 5 chunk extractions run simultaneously, then one synthesis call processes all 5
outputs. This reduces wall-clock time for Prompt 0 and makes the output of each stage testable
independently.

**Alternatives considered:**
- Single synthesis prompt watching all chunks simultaneously: rejected because it asks the
  model to do too much in one pass. Also, a single call watching a 2-hour film at full
  resolution cannot be structured to produce the granular chunk-by-chunk confidence tagging
  that the two-stage approach produces.
- Extraction only (no synthesis): rejected because 5 separate extraction logs fed directly
  to sections 1-4 would require each section prompt to perform its own reconciliation —
  duplicating the reconciliation work 4 times and producing 4 potentially inconsistent answers
  to the same reconciliation question.

**Reversal condition:** Gemini releases a model with significantly better multi-document
reasoning that makes the two-stage overhead not worth the accuracy improvement. Evaluate by
running the single-stage vs two-stage eval head-to-head on 10 reports.

---

## D-013 — WeasyPrint Over Headless Chrome for PDF Generation

**Decision:** WeasyPrint is the PDF generation library. No headless Chrome, no Playwright,
no Puppeteer.

**Rationale:** Headless Chrome requires installing a full Chromium binary in the Docker
container (~300MB), managing a browser process, and handling browser crashes and timeouts as
a worker failure mode. WeasyPrint is a pure Python library with no browser dependency, a
smaller container footprint, and simpler failure modes — it either renders the HTML or raises
an exception. WeasyPrint implements CSS print rules directly, which means `@page`, `page-break`,
and print-specific layout are handled correctly without browser rendering quirks. The PDF is
a printed document used on a clipboard — it does not need JavaScript execution or dynamic
rendering.

**Alternatives considered:**
- Playwright (headless Chrome): more CSS compatibility. Rejected because the operational
  overhead (browser process, crash handling, larger container) is not justified by the CSS
  compatibility benefit for a static print template.
- wkhtmltopdf: older, fewer dependencies than Chrome. Rejected because development has stalled,
  the print CSS support has known gaps, and WeasyPrint is the more actively maintained alternative.
- ReportLab: generates PDFs programmatically (no HTML). Rejected because the report template
  is HTML with CSS — converting it to ReportLab's canvas API would require a full rewrite
  of the template layer.

**Reversal condition:** The WeasyPrint template requires CSS features that WeasyPrint does not
support (e.g., CSS Grid in complex layouts, or specific print-only features). At that point,
evaluate Playwright with a constrained subset of CSS.

---

## D-014 — Clerk Over Auth.js / Custom Auth

**Decision:** Clerk handles all authentication. FastAPI verifies Clerk JWTs. No custom auth.

**Rationale:** Auth is not a competitive differentiator for TEX. Clerk handles signup, login,
session management, MFA, email verification, and user webhooks correctly. Building equivalent
functionality with Auth.js or custom JWT issuance is weeks of work that produces no user-facing
benefit. Clerk's webhook system (user.created, user.deleted) maps directly to the DB writes
TEX needs. The JWT verification in FastAPI is standard RS256 public key verification — no
Clerk SDK required in the backend.

**Reversal condition:** Clerk's pricing becomes prohibitive at scale (>10K MAU), or a feature
TEX needs (e.g., organization-level auth for team accounts) is not supported by Clerk.

---

## D-015 — Context Cache TTL of 1 Hour

**Decision:** The Gemini context cache created before the chord fires has a TTL of 1 hour.

**Rationale:** Sections 1-4 combined take 8-15 minutes in the parallel chord. 1 hour provides
4x headroom for retries, slow Gemini responses, and queue delays without letting the cache
accumulate unnecessary storage cost. Cache storage costs $4.50/M tokens/hour. For a 1.89M
token cache, every additional hour costs $2.13. A 1-hour TTL that covers a 15-minute window
means the cache is deleted by Google 45 minutes after it is no longer needed in the worst case.
The orchestrator also explicitly deletes the cache after sections complete — the TTL is a
safety net, not the primary cleanup mechanism.

**Alternatives considered:**
- 30-minute TTL: too tight. A section that fails and retries three times with 480-second
  backoff (8 minutes per retry) could consume 24 minutes of the TTL before sections 1-4
  complete. If retry timing pushes past 30 minutes, the cache expires mid-generation.
- 2-hour TTL: unnecessary. 1 hour already provides 4x headroom. Doubling it doubles the
  worst-case storage cost overage with no benefit.

**Reversal condition:** Section 1-4 generation times consistently exceed 45 minutes due to
Gemini latency increases or significantly longer films. Extend TTL at that point.

---

## D-016 — First Report Free Per Account, Not Per Team

**Decision:** The first-report-free gate checks `users.reports_used == 0`. One free report
per account. Not one free report per team.

**Rationale:** Per-team free reports are trivially gamed — a coach creates 10 teams and
gets 10 free reports. Per-account is clean, single-query enforceable, and cannot be gamed
without creating multiple Clerk accounts (which Clerk tracks by email and device fingerprint).
The free report is a product demo, not a permanent discount structure. One free report is
sufficient to demonstrate value. The marginal cost of the free report ($13.83 at cache miss)
is justified by the LTV of a converting coach.

**Reversal condition:** Conversion rate data shows that one free report is insufficient to
demonstrate value and coaches need two before converting. At that point, evaluate raising the
gate to `reports_used < 2`.

---

## D-017 — Technical Failure Credit, Not Stripe Refund

**Decision:** When a report fails due to a technical error after payment, the coach receives
an automatic credit (`users.report_credits + 1`), not a Stripe refund.

**Rationale:** A Stripe refund takes 5-10 business days. A credit is instant. The coach
needs to get their report — the path of least friction is a credit that lets them regenerate
immediately. A refund requires the coach to go back through checkout, which creates friction
and a negative moment in the product experience. Credits also keep the revenue in the system —
the coach will use the credit on their next report. The only coaches who prefer a refund over
a credit are coaches who have decided to stop using TEX — in which case the relationship is
already lost and the refund is the correct resolution handled case-by-case by Tommy.

**Reversal condition:** Credit usage rate falls below 50% — coaches are receiving credits
but not using them, meaning credits are not valued. At that point, add an option to request
a Stripe refund instead of using the credit.

---

## D-018 — Vertex AI Migration Executed Early (D-011)

**Decision:** Execute the D-011 Vertex AI migration now, during Phase 3, rather than at the
originally-planned Phase 5+ trigger of $2,000/month spend.

**Date executed:** 2026-04-15.

**Reason:** A Google AI Studio billing bug has been unresolved for 24+ hours and is blocking
Phase 3 and Phase 4 evals. The Developer API quota bug on context caching (tracked under task
3.17) prevents end-to-end report runs from completing. Vertex AI uses a separate quota system
tied to the GCP project, which unblocks evals immediately. Shipping Phase 3 is gated on evals
passing; waiting out the Developer API bug of unknown duration costs more than executing the
migration that was already planned.

**What changed:**
- `backend/services/ai/gemini.py` — `GeminiProvider` now branches on `GEMINI_BACKEND`
  (`developer_api` vs `vertex`). Developer API path unchanged. Vertex path uses
  `vertexai.init()` with service-account credentials, `GenerativeModel(gemini-2.5-pro|flash)`,
  `Part.from_uri(gs://..., video/mp4)`, and `vertexai.preview.caching.CachedContent` with a
  graceful sentinel fallback to direct URI passing when caching is unavailable for the model
  or SDK version.
- `backend/services/gemini_files.py` — `upload_to_gemini` / `delete_gemini_file` branch on
  `GEMINI_BACKEND`. Vertex path uploads chunks to GCS at `gs://tex-film-chunks-prod/chunks/{film_id}/{filename}`
  using `google.cloud.storage` with the same service account credentials, and returns a far-future
  sentinel `expires_at` (year 9999) so `uri_expiry.get_valid_chunk_uris` treats GCS URIs as permanent.
- `backend/services/uri_expiry.py` — explicit early-return when `GEMINI_BACKEND=vertex`:
  no re-upload scan runs. Developer API expiry logic is preserved intact.
- `backend/requirements.txt` — added `google-cloud-aiplatform>=1.71,<2.0` and
  `google-cloud-storage>=2.18,<3.0`. Kept `google-genai` so the `developer_api` backend
  remains fully functional — this is a runtime switch, not a rip-and-replace.
- `router.py`, `base.py`, all task files, all orchestrator files, and all frontend files were
  not touched. Migration is controlled entirely by the `GEMINI_BACKEND` env var.

This implements Option A of the two viable migration strategies. Option B (consolidating
upload/delete/expiry behind the `AIVideoProvider` interface in `base.py`) was considered and
rejected for this migration — see "Known tech debt" below.

**Known tech debt:** Upload, delete, and expiry-check logic still live outside the
`AIVideoProvider` abstraction, in `services/gemini_files.py` and `services/uri_expiry.py`.
`tasks/film_processing.py` and `tasks/report_generation.py` import those module-level
functions directly rather than going through `get_ai_provider()`. This means a future provider
swap would require touching the task files as well as the provider file. Option B
consolidation (moving upload/delete/expiry into `AIVideoProvider` methods, updating `base.py`,
and refactoring the tasks to call through the router) is deferred to post-launch. Acceptable
for now because the `GEMINI_BACKEND` env var already covers the migration path D-011 was
designed for, and Option B's refactor would touch files explicitly out of scope for the
eval-unblock effort.

**Reversal condition:** Not applicable — this executes the D-011 migration path earlier than
the originally-stated trigger. D-011 remains the governing decision for which backend we run
on; D-018 only documents the early execution. If Vertex AI becomes undesirable for a reason
not currently anticipated, the `GEMINI_BACKEND` switch flips back to `developer_api` with no
code changes.

---

## D-019 — pre-commit + gitleaks for local secret prevention

**Decision:** Adopt the `pre-commit` framework (https://pre-commit.com) with `gitleaks` as
the first and only hook in PR 1 of the repo hygiene cleanup. Format / lint / hygiene hooks
(`ruff`, `prettier`, `eslint`, `trailing-whitespace`, `end-of-file-fixer`,
`check-added-large-files`) land in PR 4 alongside the linter configs they enforce — keeping
PR 1 surgically scoped to security.

**Rationale:** GitHub's secret scanning + push protection are already enabled at the repo
level (confirmed in the 2026-05-17 audit) and will block known-pattern secrets server-side
on `git push`. But the failure mode they protect against — a secret committed locally, then
pushed — still pays the cost of needing to rotate the key (push protection only prevents the
public exposure, not the local commit). A pre-commit hook catches the secret before it lands
in a commit at all, eliminating the rotation cost. The two layers are complementary:
pre-commit is the first line, push protection is the safety net, Dependabot + vulnerability
scanning is the third line for dependency-introduced secrets and CVEs.

`gitleaks` (over `detect-secrets`) chosen because it has zero Python runtime dependency
(single Go binary downloaded by pre-commit on first run), ships with a maintained ruleset
that covers Stripe, GCP service accounts, Clerk JWTs, AWS / R2 keys, and generic high-entropy
patterns out of the box, and the same tool runs in the PR 3 CI workflow — one config, two
surfaces. Local hook + CI workflow is the canonical pre-commit + CI pattern; using two
different tools (e.g. `detect-secrets` locally and `gitleaks` in CI) creates surface drift
where local passes but CI fails on the same content.

**Alternatives considered:**

- `detect-secrets` (Yelp): Python-native, decent ruleset, integrates with pre-commit cleanly.
  Rejected because it requires a `.secrets.baseline` file that must be regenerated and
  reviewed on every new finding, adds a Python runtime dep to the hook, and the ruleset is
  less actively updated than gitleaks' (last meaningful rule add was 2024-Q1 vs gitleaks'
  monthly cadence).
- Bare `.git/hooks/` (no framework): rejected because git hooks are not tracked in the repo —
  they live in `.git/hooks/`, which is per-clone and per-developer. Pre-commit centralizes
  config in `.pre-commit-config.yaml` (tracked), and `pre-commit install` is a one-time setup
  per clone.
- TruffleHog: similar capability to gitleaks. Rejected on speed (heavier binary, slower scan
  on large diffs) and on the secondary point that gitleaks' ruleset is the de-facto standard
  for the pre-commit + GitHub Actions pattern, with broader community config examples.

**Reversal condition:** None anticipated. If gitleaks rules become noisy in the local workflow
(false positives on legitimate code), tune via a project-local `.gitleaks.toml` rather than
removing the hook. If a specific rule generates consistent friction, document the rationale
for the suppression in this file as a D-NNN entry.

---

## D-020 — Branch protection on main

**Date:** 2026-05-17
**Status:** Adopted

**Decision:** Enabled GitHub branch protection on `main`. Direct pushes blocked. Merges require a PR with all three CI status checks passing (`scan` from gitleaks.yml, `lint-and-compile` from backend.yml, `typecheck-and-build` from frontend.yml), branch up-to-date with main (`strict: true`), and linear history. Admin bypass disabled (`enforce_admins: true`). Force-push and deletion disabled. Additionally enabled the repo-level `delete_branch_on_merge: true` setting via `PATCH /repos/aidn31/tex-v2` so merged PR branches auto-delete from origin.

**Rationale:** Closes audit finding C1 (direct-push hole) and the auto-delete half of I4 (stale-branch accumulation). The three CI contexts define the minimum bar — secrets scan, backend lint + compile, frontend typecheck + build — that every change to main must clear. Strict mode forces rebase-before-merge, preserving linear history (per D-019's hygiene posture). Required-approving-review-count is 0 because this is a solo repo — Tommy cannot self-approve, and adding a "1 review required" rule would deadlock all merges. `delete_branch_on_merge` paired with the I4 stale-branch deletions resolves the full I4 finding: past stale branches removed, future stale-branch accumulation structurally prevented.

**Tradeoff:** With admin bypass disabled, emergency hotfixes require temporarily disabling protection via the API (`gh api --method DELETE /repos/aidn31/tex-v2/branches/main/protection`, hotfix, then re-PUT the same JSON) rather than force-pushing. Acceptable for a solo proprietary repo with no live customers — the operational cost is small and the structural guarantee is large. Revisit if first paying customer onboards and incident response time becomes load-bearing.

---

## D-021 — Linter and formatter configs

**Date:** 2026-05-17
**Status:** Adopted

**Decision:** Adopted `ruff` (E/F/W/I/UP/B rules) + `mypy` (`strict=false` baseline) for backend, `eslint` (flat config, ESLint 9) + `prettier` for frontend. All four tools wired into both `.pre-commit-config.yaml` (local) and `.github/workflows/{backend,frontend}.yml` (CI gate). Versions pinned identically across local and CI:

- `ruff == 0.15.13`
- `mypy == 2.1.0`
- `eslint == 9.39.4`
- `typescript-eslint == 8.59.3`
- `eslint-config-next == 15.5.18` (tracks Next.js major)
- `prettier == 3.8.3`
- `@eslint/eslintrc == 3.3.5` (FlatCompat shim — see Tech debt below)

`pyproject.toml` lives at `backend/pyproject.toml` (not repo root) to keep backend tooling co-located with the backend code.

**Rationale:** Closes audit findings I1 (full — pre-commit framework with gitleaks + hygiene + ruff/mypy/eslint/prettier hooks), I2 (Python lint/typecheck config), I3 (frontend lint/format config). Pre-PR-4, the only enforced rules were ruff F (unused-imports only) and gitleaks — anything else was on the honor system.

**Tightening path:** mypy starts permissive (`strict=false`, `ignore_missing_imports=true`, `warn_return_any=true`, `warn_unused_ignores=true`, `check_untyped_defs=true`) to land the gate without a 500-finding backlog. Tighten gradually — first enable `strict-optional`, then `disallow_untyped_defs` per-module, then full `strict`. Each tightening step is its own PR.

**`any` policy:** New code must not use `any` (eslint enforces `error` level). PR 4's surface scan found zero pre-existing `any` usages, so no bulk ignore-with-TODO sweep was needed.

**B008 scoping:** FastAPI's `Depends()` / `Body()` default-argument pattern is the canonical reason B008 fires. Scoped via `[tool.ruff.lint.per-file-ignores]` to `routers/*.py` + `services/clerk.py` (the dependency-injection sites); B008 remains enforced globally everywhere else where it catches real mutable-default-arg bugs.

**`react-hooks/exhaustive-deps`:** Surfaced as 9 pre-existing warnings on PR 4 baseline. Left as plain ESLint warnings (CI exits 0 on warnings) rather than ignore-with-TODO + issues — the rule is too noisy to justify per-warning tracking, and the right discipline is "review when next touching the file." Lint output visibility is the tracking mechanism.

**Tech debt:**

- **ESLint flat-config bridge:** `eslint-config-next@15` still exports in legacy `.eslintrc` format and depends on `@rushstack/eslint-patch`, which is incompatible with ESLint 9's module resolution. Bridged via `@eslint/eslintrc` `FlatCompat` shim in `frontend/eslint.config.mjs`. Remove the shim and the dep once `eslint-config-next` ships native flat-config support.
- **Vertex SDK + google-cloud-storage stub gaps:** 4 type-ignored sites in `services/ai/gemini.py` and `services/gemini_files.py`. Each anchored to a GitHub issue (#19–#22) with the condition for dropping the ignore.

---

## D-022 — Repository documentation

**Date:** 2026-05-18
**Status:** Adopted

**Decision:** Added `README.md` at repo root (front door only — no duplication of canonical docs), `frontend/.env.example` (mirrors `backend/.env.example` for parity), and `.github/pull_request_template.md` (short checklist). No `LICENSE` — repo is proprietary, all rights reserved.

**Rationale:** Closes audit findings P1 (no README), P3 (no PR template), P4 (no frontend `.env.example`). Tommy explicitly chose to leave LICENSE absent rather than add MIT/Apache (P2 — closed by decision, not by file).

**README scope:** Strictly a front door. Any temptation to summarize architecture, stack, or roadmap in README is wrong — those have their own files, and duplication creates drift. Anything beyond "what is TEX, how to run it, where to read next" belongs elsewhere. The PR 4 README that introduced a "Local development" section is superseded by PR 5's wholesale-replacement README; the same essential content is preserved, but the structure now matches the front-door scope this entry codifies.

**`frontend/.env.example` scope:** Document every env var actually referenced by the frontend code today. Reserved-but-unused vars (Stripe publishable key, PostHog) are commented-out with a short note on what unlocks them — kept in the file so future contributors know the names, but disabled so they don't read as required.

---

## D-023 — Prompts 0A/0B v1.6 documented as canonical baseline

**Date:** 2026-05-19
**Status:** Adopted

**Decision:** Prompts 0A (`chunk_extraction.txt`) and 0B (`chunk_synthesis.txt`) at **`VERSION: v1.6`** are documented in PROMPTS.md as the canonical baseline for the Stage-1 commercial-readiness gate. The §STAGE 1 and §STAGE 2 fences in PROMPTS.md are re-mirrored verbatim from the `.txt` files (no more "v1.0 baseline mirror" notes). The composite cache key derivation (`{sections_v}|{preprocess_v}` from `services/prompt_versions.py`) is documented in the PROMPT VERSIONING PROTOCOL section, including the `+` join behavior when 0A and 0B diverge and the `offensive_sets.txt`-as-sentinel rule for the 6-section bundle.

**Rationale:** The drift report (`docs/drift-report-2026-05-19.md`) flagged PROMPTS.md as stale on three counts: (a) version markers at v1.5 instead of v1.6, (b) mirrored bodies frozen at the v1.0 baseline (6 revisions behind), and (c) cache-key composition mechanism undocumented anywhere. The half-mirror state was the worst of both worlds — readers could copy-paste a baseline that hadn't been the production prompt for months. Documenting v1.6 as canonical and synchronizing the mirrors closes the drift; documenting the cache-key mechanism prevents future prompt edits from silently failing to invalidate stale cached work.

**Tightening path:** Subsequent prompt revisions (v1.7+) must update the mirror in PROMPTS.md in the **same PR** as the `.txt` edit. Reviewers should reject any prompt-`.txt` change whose PR diff does not also touch PROMPTS.md's mirrored body. The "under redesign" language has been removed from PROMPTS.md; further post-eval iteration of Prompts 0A/0B is tracked in **GitHub Issue #28** and will be re-canonicalized in this file once the Step-6 eval threshold lands a stable version.

**Reversal condition:** None for the documentation discipline itself. The specific v1.6 body is reversible — bump to v1.7+ in `.txt` files, mirror to PROMPTS.md in the same PR, log under D-NNN if the rationale is significant.

---

## D-024 — Synthesis-only mode (Option 3) adopted as canonical architecture

**Date:** 2026-05-19
**Status:** Adopted

**Decision:** Report-generation sections 1-4 read the `synthesis_document` produced by Prompt 0B as **text context**, not the raw chunk video. The pipeline is: Prompt 0A processes each chunk's video once → Prompt 0B synthesizes all extractions into a unified document → sections 1-4 (Gemini 2.5 Pro) receive [synthesis_document + roster] as text Parts → sections 5-6 (Gemini 2.5 Flash, Claude fallback) build on sections 1-4 text. Google's `CachedContent` API is **not** used at report-generation time; `services/ai/gemini.py::create_context_cache()` returns a local `vertex:no-cache:<json>` sentinel encoding the text payload. Chunk video is consumed exactly once in the pipeline, during `extract_chunk`.

**Rationale:** The original design (Gemini CachedContent built from chunk URIs, shared across sections 1-4) hit Google's context-caching quota in a way that blocked Phase 3 evals (see D-018 history). Switching to a text-first architecture, with Prompt 0A doing the perception work and Prompt 0B reconciling, produced a stable, debuggable pipeline that decouples TEX from Google's caching quirks. The synthesis document is also a better unit of grading: it can be smell-tested against the golden-set ground-truth docs directly, independent of section-prompt drift. With this architecture stable, the original "video-to-cache-to-sections" design is no longer the target; switching back would require fresh evaluation, not just enabling a flag.

**What this changes:**
- `services/ai/gemini.py::create_context_cache()` returns the `vertex:no-cache:<json>` sentinel; sections 1-4 call `analyze_video_cached()` which sends `[text_context, prompt]` to Gemini 2.5 Pro.
- Rate-limit buckets and Prompt-0A token cost dominate the per-film unit-cost equation (re-modeled in COSTS.md in PR 3 of the doc refresh).
- ARCHITECTURE.md report pipeline + pipeline intelligence map + AI provider abstraction rewritten in PR 2 of the doc refresh.
- AGENTS.md `run_synthesis_sections` cleanup logic updated to skip Google-cache deletion when `cache_uri` is a sentinel.

**Alternatives considered:**
- Stay on Google CachedContent and wait out the quota issue: rejected — quota timing was unknown and the eval grind was blocked.
- Hybrid (video for some sections, text for others): rejected as more complex for unclear benefit; revisit only if eval results show sections that demonstrably need raw video re-reading.

**Reversal condition:** Future evaluation shows that re-introducing chunk video alongside the synthesis document materially improves accuracy on a section that the synthesis-only path under-serves (most likely candidate: player_pages, where individual-player observation may benefit from re-watching). At that point: re-introduce a real cache or per-section video Parts behind the same `analyze_video_cached()` interface — the abstraction is built for this. Until that evaluation runs and produces evidence, synthesis-only is the architecture.

---

## D-025 — Graceful synthesis degradation removed; synthesis_failed column unused

**Date:** 2026-05-19
**Status:** Adopted

**Decision:** If `run_chunk_synthesis` (Prompt 0B) fails after all retries, the film transitions to `status='error'` and the coach is notified. Sections 1-4 are **not** attempted without the synthesis document. The previously-documented "graceful degradation" path (set `films.status='processed'`, set `films.synthesis_failed=true`, run sections 1-4 against raw video and roster) is removed from the architecture. The `films.synthesis_failed boolean` column in `migrations/004_create_films.sql` becomes dead schema; it will be dropped in a future migration.

**Rationale:** The degradation path was designed for the original video-fed-sections architecture (D-024). Under that design, raw video plus roster was already the section 1-4 input — the synthesis document was an enrichment. When sections were demoted to text-only input (D-024), the synthesis document became the input. There is no longer a "without the synthesis document" path that produces useful section output; what sections 1-4 receive in synthesis-only mode is the synthesis document. Pretending otherwise produces empty reports the coach has to refund anyway. Failing loudly on synthesis failure is the correct behavior — the failure credit (D-017) ensures the coach is made whole. Cleaner failure mode, fewer states to reason about.

**What this changes:**
- AGENTS.md `run_chunk_synthesis` step 7 documents `status='error'` on final retry.
- ARCHITECTURE.md report pipeline + AI provider abstraction reflect "synthesis_document is required for sections 1-4."
- `films.synthesis_failed` column is documented in SCHEMA.md but marked unused; a future migration will drop it (no rush — it's a single boolean column, harmless to leave).

**Alternatives considered:**
- Keep the degradation path and accept low-quality sections 1-4 on synthesis failure: rejected — coach experience worse than a clean failure + credit.
- Add a fallback Prompt 0B (e.g., simpler synthesis on Claude): not needed at current scale; if Prompt 0B reliability becomes a problem, evaluate then.

**Reversal condition:** Synthesis failure rate is high enough that the coach-facing impact (films failing terminally) outweighs the cost of providing a degraded report. At current rates this is hypothetical.

---

## D-026 — process_film hard timeout fixed at 120 minutes

**Date:** 2026-05-19
**Status:** Adopted

**Decision:** `process_film` runs with `soft_time_limit=7000` (~117 min) and `time_limit=7200` (120 min). The previous configuration of 55/60 minutes is removed. Optimizing FFmpeg compression speed inside the Docker for Mac dev environment is **not** on the critical path — the timeout adjustment accepts the slow case rather than re-engineering the compression pipeline pre-launch.

**Rationale:** Empirically, FFmpeg's H.264 re-encode runs ~10× slower in Docker for Mac than native macOS (no VideoToolbox hardware acceleration inside the Linux VM). A 2-hour 1080p film can spend 40+ minutes on compression alone, followed by chunk uploads and Prompt 0A extraction per chunk. The original 60-minute hard limit consistently false-positive-killed real Film 04 runs in dev. Production Cloud Run workers do not have the Docker for Mac performance penalty (Linux x264 software encoding on Cloud Run CPU allocations is fast enough), but the doubled timeout is a safe ceiling for both environments and for genuinely long inputs. The trade-off vs the original 60-minute limit is: detection latency for a stuck task goes from ~60 minutes to ~120 minutes. Acceptable — startup recovery + dead-letter alerts catch persistent stuck tasks anyway, and a stuck task can be killed manually from the admin UI faster than waiting for the hard limit.

**What this changes:**
- AGENTS.md timeout reference table: `process_film` row says 117/120 min.
- ARCHITECTURE.md Celery section: timeout box says 117/120 min, with the Docker-for-Mac rationale explained.
- `backend/tasks/film_processing.py`: `soft_time_limit=7000`, `time_limit=7200`. Error string updated to "Processing timed out after 120 minutes" (both `_write_dead_letter` call and `_update_film_status` call).

**Alternatives considered:**
- Engineer faster compression (e.g., NVENC on a GPU worker, or pre-compress at upload time): rejected — out of scope pre-launch. The compression cost itself is also fine; it's only the dev-loop ergonomics that degraded.
- Skip compression entirely for files under 2GB and force coaches to compress before upload: rejected — adds friction for the coach.

**Reversal condition:** Production Cloud Run runs show `process_film` consistently completing under 60 minutes, AND the dev environment moves to a setup that doesn't pay the Docker-for-Mac penalty (e.g., native dev, or a Linux dev VM with HW acceleration). At that point, tightening the limit back toward 60 minutes restores faster stuck-task detection.

---

## D-027 — FFmpeg compress subprocess timeout raised to 7000s

**Date:** 2026-05-23
**Status:** Adopted

**Decision:** `compress_film` in `backend/services/ffmpeg.py` runs the FFmpeg subprocess with `timeout=7000` (~117 min). Previous value was `timeout=3600` (60 min). The error message changes from "Film compression timed out after 60 minutes." to "Film compression timed out after 117 minutes."

**Rationale:** The 3600s value was an undocumented guess that pre-dated empirical measurement on production-realistic film sizes. Three real-world 1080p game films (3-4 GB) failed today against the 60-minute subprocess limit even though the parent Celery `process_film` task had budget remaining (D-026 set `soft_time_limit=7000` / `time_limit=7200`). Raising the inner subprocess limit to 7000s lines it up just under the parent task's soft limit, giving a single coherent timeout boundary instead of two competing ones. `split_film`'s 1800s timeout is untouched — splitting runs on already-compressed files and 30 min is comfortably enough.

**Alternatives considered:**
- Leave at 3600s and require coaches to pre-compress: rejected — adds upload friction, undermines "drop your raw film in" UX.
- Lift to 7200s (match parent hard limit): rejected — leaves no headroom for the parent to surface a clean Celery timeout error vs. a subprocess kill. 7000s keeps ~3 min of parent margin.

**Reversal condition:** Production Cloud Run compression runs consistently complete in well under 60 minutes AND a smaller timeout would catch real stuck-FFmpeg cases faster than the existing watchdog. At that point, tighten back toward 3600s.

---

## D-028 — Admin-only film retry endpoint

**Date:** 2026-05-23
**Status:** Adopted

**Decision:** New route `POST /admin/films/{film_id}/retry` (admin-gated via `require_admin`) re-enqueues `process_film` for a film stuck in `status='error'` without requiring the coach to re-upload. The handler resets `status='uploaded'`, `gemini_processing_status=NULL`, `chunk_count=NULL`, `synthesis_failed=FALSE`, `error_message=NULL`, `updated_at=now()` in a single transaction and calls `process_film.delay(film_id)`. Returns 404 (not found), 409 (status not 'error'), 400 (missing r2_key), or 202 Accepted. Automatic retry with exponential backoff is deferred as a future enhancement.

**Rationale:** When `process_film` fails terminally (e.g., the D-027 timeout case before today's fix, or transient Gemini File API errors), the R2 object is still present and the film row already has the right ids — only the processing-state columns need to be cleared. Forcing the coach to re-upload a 4 GB film over residential bandwidth to recover from a server-side failure is a worse experience than an admin clicking a button. Admin-only because the failure-credit policy (D-017) already handles the coach-facing case; this endpoint is for operator recovery, not user self-service. The user-facing `POST /films/{film_id}/retry` route already exists for coach self-service on their own films — the admin route is parallel but scopes by `film_id` only (no `user_id` filter), so admins can recover films owned by any coach.

**Alternatives considered:**
- Reuse the user-facing `/films/{film_id}/retry` and require admins to impersonate the coach: rejected — impersonation flow doesn't exist and adding one for this is overkill.
- Build full auto-retry with exponential backoff now: rejected for v1. Most failures we've seen are either (a) timeouts that won't resolve without code changes or (b) transient API errors that succeed on a single manual retry. Auto-retry adds complexity (jitter, max-attempt accounting, dead-letter interaction with the existing watchdog) for an unclear win pre-launch. Revisit once we have data on failure-cause distribution.
- Allow retry on non-'error' statuses (e.g., re-process a 'processed' film against a new prompt): rejected — that's a different operation ("re-extract") that should be its own endpoint with its own semantics. Keeping retry narrow prevents accidental double-processing.

**Reversal condition:** Failure rate stabilizes low enough that manual operator retry is no longer the bottleneck, OR a clear pattern of transient-only failures emerges that auto-retry could handle without operator involvement.

---

## D-029 — Raised process_film Celery time limits from 7000/7200s to 14000/14400s

**Date:** 2026-05-23
**Status:** Adopted

**Decision:** `process_film` in `backend/tasks/film_processing.py` runs with `soft_time_limit=14000` (~233 min) and `time_limit=14400` (240 min = 4 hours). Previous values were `soft_time_limit=7000` / `time_limit=7200` set in D-026.

**Rationale:** Yesterday (D-027) we raised the inner FFmpeg subprocess timeout from 3600s to 7000s to fix three films failing during compression. Today, two more films failed with `SoftTimeLimitExceeded` while still mid-compression — the outer Celery wrapper was the next binding constraint, not the inner subprocess. Empirical observation: Brad Beal Elite and Florida Rebels both hit the limit at exactly 117 min (the 7000s soft mark) while FFmpeg was still re-encoding. The 7000/7200 budget from D-026 was sized to cover compression alone; it left no room for the rest of the pipeline (R2 download + FFprobe validate + split + chunk upload to Gemini File API + DB writes). 4-hour budget reflects the real-world worst case (large file + slow CPU + chunk uploads over residential bandwidth) with margin, while still being short enough that a genuinely stuck task — e.g., infinite loop, deadlock — eventually surfaces.

**What this changes:**
- `backend/tasks/film_processing.py` decorator on `process_film`: `soft_time_limit=14000`, `time_limit=14400`.
- AGENTS.md timeout reference table for `process_film` will need to be updated to 233/240 min (out of scope for this PR — flagged as follow-up doc work).
- Existing error strings in `film_processing.py` lines 452 + 458 still read "Processing timed out after 120 minutes" — also out of scope per the narrow brief, flagged as follow-up.

**Alternatives considered:**
- Tighter budget (e.g., 10800/11000 = 3 hours): rejected — only ~30-min margin over today's empirical fail point. Not enough headroom for unfavorable network conditions or larger films coaches may upload (some EYBL film sources export 1080p60 at >4 GB).
- Auto-retry with exponential backoff: noted as deferred in D-028. Doesn't solve the underlying need — a task that times out at 7000s also times out at 7000s on retry. Backoff helps for transient API errors, not for "the pipeline genuinely takes longer than the budget."
- Pre-compression on the coach's device before upload: rejected — adds significant UX friction and defeats the "drop your raw film in" core value prop. Some coaches don't have tools (or know-how) to re-encode locally.

**Reversal condition:** Production Cloud Run workers (with proper CPU allocations, not Docker for Mac) consistently complete `process_film` in well under 90 minutes, AND we've seen no large-film tail-latency cases that approach the new ceiling. At that point, tighten back toward a 2-hour budget so stuck-task detection latency improves.

---

## DECISION PROTOCOL FOR FUTURE DECISIONS

When a new architectural decision is needed:

1. Stop. Do not implement until the decision is documented here.
2. State the decision being made in one sentence.
3. Write the rationale — why this option over others.
4. List alternatives considered and why they were rejected.
5. State the reversal condition — what evidence would cause this decision to be revisited.
6. Get Tommy's explicit approval.
7. Add the entry to this file with the next D-NNN number.
8. Then implement.

A decision made without a DECISIONS.md entry is an undocumented decision.
Undocumented decisions get reversed accidentally when context is lost between sessions.

---

*Last updated: May 23, 2026 — D-029 added (process_film Celery limits raised 7000/7200s → 14000/14400s after empirical 117-min fail point on real films).*
*29 decisions logged. All decisions current as of this date.*
