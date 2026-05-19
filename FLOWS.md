# FLOWS.md — TEX v2

End-to-end user flows. Every screen a coach sees, every state it can render, every action
they can take. The corresponding backend behavior is described alongside the UX because
flows like film upload and report generation cross the frontend/backend boundary.

Read PRD.md before this. Read ARCHITECTURE.md for the report pipeline and AGENTS.md for
the Celery task graph.

**Canonical prompt versions: 0A v1.6, 0B v1.6 (see PROMPTS.md) (tracked in Issue #28).**

---

## HOW TO READ THIS DOCUMENT

Each flow section covers:
- **Route** — the URL path (frontend) and/or API endpoint (backend)
- **States** — every possible state the screen can render
- **Actions** — what the coach can do
- **Empty / error states** — what shows when there's no data or something fails

The frontend is a thin client. It renders state and calls the backend. It does not compute.

---

## ROUTE MAP — FRONTEND

```
/sign-in                                — Clerk-hosted login
/sign-up                                — Clerk-hosted signup
/dashboard                              — coach home: teams list, recent films, inline notifications
/teams/[id]                             — single team: roster + films + reports tabs
/upload?team_id=[id]                    — film upload (single presigned PUT to R2)
/reports/[id]                           — report status + PDF download
/admin                                  — admin home (is_admin-gated): corrections page
/admin/patterns                         — pattern analyzer
/admin/users                            — user management
```

Routes that previously appeared in this doc but **do not exist on disk**:
- `/teams` (no list page — dashboard is the teams list)
- `/admin/corrections` (corrections live at `/admin` itself; the admin nav labels `/admin` as "Corrections")
- `/admin/dead-letters` (no UI built)

## ROUTE MAP — BACKEND (relevant for these flows)

```
POST   /films/upload-initiate           Create films row, return single presigned PUT to R2
POST   /films/upload-complete           Mark film uploaded, enqueue process_film
POST   /films/upload-abort              Cancel + cleanup
POST   /films/{id}/retry                Re-enqueue process_film for a film in error state
GET    /films/                          List films for current user
GET    /films/{id}                      Get one film's status
POST   /reports                         Create report — returns either {report_id} (free/credit) or {payment_required: true}
GET    /reports                         List reports for current user
GET    /reports/{id}                    Get one report (includes embedded pdf_url when complete)
POST   /stripe/create-checkout-session  Create Stripe Checkout (paid path)
POST   /stripe/webhook                  Stripe webhook (checkout.session.completed → enqueue generate_report)
POST   /webhooks/clerk                  Clerk Svix webhook (user.created, user.deleted)
GET    /notifications/                  List notifications (frontend filters unread client-side)
POST   /notifications/{id}/read         Mark a notification read
POST   /notifications/read-all          Mark all read (API exists; no UI calls it)
GET    /admin/corrections, /admin/pattern-analysis, /admin/users (is_admin-gated)
POST   /admin/corrections, /admin/users/{id}/credits
POST   /dev/seed-user                   Local-dev Clerk webhook stand-in (gated by environment)
```

---

## FLOW 1 — AUTH

### Sign Up (`/sign-up`)

Clerk-hosted component. TEX does not build this screen.

**After sign-up:**
- Clerk fires `user.created` webhook → FastAPI inserts row into `users` table.
- In **local dev**, the Clerk webhook is unreliable through ngrok. The dashboard and admin
  layout call `POST /dev/seed-user` on mount in development mode to ensure the local user
  row exists.
- Coach is redirected to `/dashboard`.

### Sign In (`/sign-in`)

Clerk-hosted. Redirects to `/dashboard` after success.

### Auth Gate

Every route except `/sign-in(.*)` and `/sign-up(.*)` is behind Clerk's middleware
(`frontend/middleware.ts`). Unauthenticated requests redirect to `/sign-in`. Admin routes
additionally check `is_admin` from the DB on every request (`services/clerk.py::require_admin`).

---

## FLOW 2 — ONBOARDING (FIRST-TIME COACH)

**Trigger:** Coach lands on `/dashboard` with zero teams.

**Screen shows:**
- Welcome message and three-step visual guide: Create a team → Add a roster → Upload film.
- CTA button: **"Create Your First Team"** → opens the New Team modal.

**Rules:**
- This is a guide, not a gated wizard.
- Once the coach has at least one team, the onboarding prompt is never shown again.

---

## FLOW 3 — DASHBOARD (`/dashboard`)

### States

**State A — Has teams:**
- List of team cards (name, level, film count, last-report date).
- "New Team" button → opens the New Team modal (Flow 4).
- Each card links to `/teams/[id]`.

**State B — No teams (first visit):**
- Onboarding prompt (Flow 2).

**State C — Notifications inline:**
- Unread notifications render as a banner-style list at the top of the dashboard
  (not a nav-bar dropdown — there is no nav bar in the current UI).
- Each item has View / Dismiss actions; Dismiss calls `POST /notifications/{id}/read`.
- The dashboard loads notifications once via `GET /notifications/` and filters unread client-side.

**State D — Recent Films:**
- Last 5 films across all the coach's teams render as a "Recent Films" list below the
  teams grid. Each shows team name, file name, status badge, upload date.

**State E — Couldn't load:**
- Backend reachability or expired-session failure shows an inline error with a Retry button
  and an explanation pointing at backend reachability / sign-in.

### Polling

The dashboard does **not** poll for report progress. Polling happens only on the report
detail page (Flow 8). A coach who navigates away will see the completed-report notification
on their next dashboard visit, or via the in-app notification banner.

---

## FLOW 4 — CREATE TEAM (MODAL)

**Trigger:** "New Team" button on dashboard.

**Modal fields:**
- Team name (required, max 100 chars).
- Competition level (required, dropdown): D1 / D2 / D3 / EYBL / EYBL Scholastic / AAU /
  High School / Unknown.

**Actions:**
- Submit → `POST /teams` → modal closes, card appears in list.
- Cancel → modal closes, no change.

**Validation (inline, before submit):**
- Empty name → "Team name is required"
- Name over 100 chars → "Team name is too long"
- No level → "Please select a competition level"

**Error state:**
- API error → "Something went wrong. Try again." inline. Do not close the modal.

---

## FLOW 5 — TEAM PAGE (`/teams/[id]`)

Three tabs: **Roster** / **Films** / **Reports**.

### Header

- Team name + competition level.
- "Edit Team" → inline name/level edit.
- "Delete Team" → confirmation modal: *"Delete [Team Name]? This cannot be undone."*
  Soft delete (`teams.deleted_at`).

### Tab: Roster

**State A — Has players:**
- Table columns: #, Name, Position, Height, Role, Actions.
- Delete icon per row → confirmation: *"Remove #{jersey} {name}?"*
- "Add Player" button → opens an inline form.

**State B — No players:**
- Empty state: *"No players yet. Add your roster so TEX can identify players in the film."*
- "Add Player" button.

**Add/Edit player fields (as currently implemented):**
- Jersey # (required, text — allows "00", "0", "33A")
- Full name (required, text, max 60 chars)
- Position (optional, **free-text input** — not a dropdown today)

The roster table renders the columns above. Additional fields exist in the schema
(`dominant_hand`, `role`, `height`, `notes`) and in the API client types but are **not
exposed in the current Add/Edit form**. Adding the missing inputs is a future UX task.

**Validation:**
- Duplicate jersey on same team → "Jersey #{X} is already on this roster" (backend returns 409).
- Empty name → "Player name is required".

### Tab: Films

**State A — Has films:**
- List of film cards: file name, upload date, duration, status badge.
- Status badges (cover all states from `films.status`):
  - `Uploaded` — in R2, awaiting process_film
  - `Processing` — process_film running
  - `Chunks Uploaded` — chunks in Gemini File API; extract_chunk in progress
  - `Processed` — synthesis_document written; ready for report generation
  - `Error` — terminal failure (timeout, validation, synthesis failure)
- "Upload Film" button → navigates to `/upload?team_id=[id]`.

**State B — No films:**
- Empty state: *"No films uploaded yet for this team."*
- "Upload Film" button.

**Film card actions:**
- If status = `error`: "Retry" button → `POST /films/{id}/retry`.
- No per-film "Generate Report" button — a single "Generate Report" button appears at the
  bottom of the Reports tab once at least one film is `processed`.
- No film delete UI is built today. (The `films.deleted_at` column exists for future use.)

### Tab: Reports

**State A — Has reports:**
- List of report cards: date generated, status badge, section count.
- Status badges: `Pending` (yellow) → `Processing` → `Complete` / `Partial` (yellow) / `Error`.
  - `Partial` is a real terminal state — assemblies where 1-5 sections errored. PDF still delivered.
- Complete reports show "Download PDF" — links to the embedded `pdf_url` in the
  `GET /reports/{id}` response (15-minute presigned R2 URL).

**State B — No reports:**
- Empty state: *"Upload a film and wait for it to process before generating a report."*
  Shown only when both `reports.length === 0` and no `processed` films exist.

---

## FLOW 6 — FILM UPLOAD (`/upload?team_id=[id]`)

### Step 1 — Select File

**Screen shows:**
- Drag-and-drop zone.
- Accepted formats: **MP4, MOV, AVI, WebM** (browser MIME check).
- No file-size ceiling displayed; no client-side size check enforced.

**Client-side validation:**
- Wrong file type → *"Only video files are accepted (MP4, MOV, AVI, WebM)"*
- That's the only client-side check. Size and duration limits are enforced server-side
  (duration check is FFprobe in the worker, not the upload page).

### Step 2 — Uploading

**Single presigned PUT to R2** (not a multipart upload):

1. Frontend calls `POST /films/upload-initiate` with `{team_id, file_name, file_size_bytes}`
   → backend creates a `films` row (`status='uploaded'` placeholder) and returns
   `{film_id, r2_key, upload_url}`. The `upload_url` is a presigned PUT valid for 1 hour.
2. Frontend `xhr.open('PUT', upload_url)` streams the file to R2 with progress events.
3. On upload success, the frontend fetches a fresh Clerk JWT (long uploads can outlive
   the ~60s token TTL) and calls `POST /films/upload-complete` with `{film_id}` → backend
   marks the film and enqueues `process_film`.
4. On upload failure or user cancel, frontend calls `POST /films/upload-abort`.

**Screen shows:**
- File name + size.
- Progress bar — percent complete.
- No ETA, no Cancel button (these were spec'd but never built; flagged for future UX work).

**Retry:**
- The presigned PUT is a single XMLHttpRequest. There is no automatic part-retry — a
  failed PUT surfaces the error state below.

### Step 3 — Done

**Screen shows:**
- *"Film uploaded. TEX is processing your film."*
- "Go to Dashboard" link.

The upload page does **not** poll for processing progress. Polling lives on the team page
(Films tab), which refreshes film statuses every 10 seconds while any film is in a non-terminal
state. A coach can navigate away and check back from the dashboard.

### Error States

| Error | Message shown |
|---|---|
| Upload PUT failure | *"Upload failed. Check your connection and try again."* + Retry button |
| File validation failure (worker FFprobe) | *"TEX couldn't process this file: [reason]."* surfaced on the team page Film card |
| Film too short (<60s) | FFprobe rejects: `films.status='error', error_message="Film is under 1 minute. Not valid game film."` |
| Film too long (>3 hr / 10800s) | FFprobe rejects: `films.status='error', error_message="Film exceeds 3-hour limit."` |
| No video stream | FFprobe rejects: `films.status='error', error_message="File contains no video stream."` |
| process_film timeout (120 min hard kill, D-026) | `films.status='error', error_message="Processing timed out after 120 minutes"` |
| Prompt 0B (run_chunk_synthesis) failure | `films.status='error', error_message="Synthesis failed: ..."` per D-025 — no graceful degradation |

The upload page itself is static after step 3. Error states for downstream processing are
visible on the team page Films tab and as in-app notifications.

### No-team-selected state

If the coach navigates to `/upload` without a `team_id` query param, the page renders
*"No team selected."* with a Dashboard link.

---

## FLOW 7 — GENERATE REPORT

**Trigger:** Coach clicks "Generate Report" at the bottom of the Reports tab on a team
page once at least one film is `processed`.

### Two paths from one endpoint

`POST /reports` is the entry point in both cases. The response distinguishes:

```
{ payment_required: false, report_id, status: "processing" }    → free or credit path
{ payment_required: true,  team_id, film_ids }                  → Stripe required
```

### Free / credit path

If `users.reports_used == 0` (first report ever — D-016) or `users.report_credits > 0`:

1. `POST /reports` returns `{payment_required: false, report_id}`.
2. Backend records the report, decrements the credit (or increments `reports_used`), and
   enqueues `generate_report`.
3. Frontend navigates to `/reports/[id]` (Flow 8).
4. `run_chunk_synthesis` already ran during film processing — its output
   (`film_analysis_cache.synthesis_document`) is the input to sections 1-4. **No
   auto-trigger** happens at synthesis completion (D-024 architecture; see AGENTS.md and
   ARCHITECTURE.md). Report generation is always coach-initiated or webhook-initiated.

### Paid path

If neither free nor credit applies:

1. `POST /reports` returns `{payment_required: true, team_id, film_ids}`.
2. Frontend calls `POST /stripe/create-checkout-session` → receives `{checkout_url, payment_id}`.
3. Browser navigates to Stripe Checkout.
4. **On success:** Stripe redirects to `/dashboard?checkout=success`. Stripe also fires
   `checkout.session.completed` to `POST /stripe/webhook`:
   - Webhook handler verifies signature, marks payment complete, creates the report,
     enqueues `generate_report`.
5. **On cancel:** Stripe redirects to `/dashboard?checkout=cancel`. No report is created.

Once `generate_report` is enqueued (either path), Flow 8 takes over.

### Section-cache short-circuit (regeneration of an existing report on cached film)

If the report is single-film and `film_analysis_cache.sections` already has section 1-4
content at the current composite `prompt_version`:

- `generate_report` skips the section_generation chord entirely.
- Sections 1-4 are written to `report_sections` with `model_used='cached'`.
- `run_synthesis_sections` is invoked directly to run sections 5-6.

This makes report regeneration near-free for unchanged films at unchanged prompts (see
COSTS.md "Two-Layer Caching"). The coach sees the same status flow as a cold report;
just faster.

---

## FLOW 8 — REPORT STATUS (`/reports/[id]`)

### States

**State A — Pending / Processing:**
- *"Generating your scouting report…"*
- Section progress tracker in canonical order:
  ```
  Offensive Sets               [status]
  Defensive Schemes            [status]
  Pick and Roll Coverage       [status]
  Individual Player Pages      [status]
  Game Plan                    [status]
  Adjustments & Practice Plan  [status]
  ```
  Each row shows status (`pending` / `processing` / `complete` / `error`) and, once
  complete, the `model_used` and `generation_time_seconds` (e.g. `gemini-2.5-pro · 42s`).
- Polls `GET /reports/{id}` **every 10 seconds** while status is non-terminal.

**State B — Complete:**
- *"Your scouting report is ready."*
- "Download PDF" button → opens the `pdf_url` in the report response in a new tab.
  The pdf_url is a 15-minute presigned R2 URL; the response includes it inline (no
  separate `/reports/{id}/download` endpoint exists).
- Report metadata: team name, date generated, films used, total `generation_time_seconds`.
- Per-section preview: `model_used` and `generation_time_seconds` under each completed row.

**State C — Partial:**
- Yellow badge: `Partial`.
- *"Your report is ready with some sections incomplete."*
- Download PDF available — the PDF contains placeholder pages for failed sections.

**State D — Error:**
- *"Report generation failed."*
- `error_message` from the `reports` row.
- No "Try Again" button is built today — the coach goes back through Flow 7 to retry.
  (A failure credit was automatically applied per D-017, so a paid retry is free.)

### Polling Rules

- Poll every 10 seconds while status is `pending` or `processing`.
- Stop polling when status becomes `complete`, `partial`, or `error`.
- No WebSockets. Polling is sufficient for 15-50 minute report times.

### Error reasons surfaced

| Error | Source |
|---|---|
| All sections errored | `_handle_all_sections_errored` in `run_synthesis_sections`; failure credit applied |
| All sections errored after partial assembly | `assemble_and_deliver` `error_count == 6` path; failure credit applied |
| Generation timeout | `generate_report` hard kill (30 min) — rare; usually individual section retries fail first |
| Section retry exhaustion | A single section's `dead_letter_tasks` row + `report_sections.status='error'` — report continues with placeholder, ends `partial` |
| Synthesis failure (upstream) | Film transitions to `status='error'`. Report cannot run. Per D-025, no graceful degradation |

---

## FLOW 9 — IN-APP NOTIFICATIONS

**Trigger events that produce notifications:**

```
type=report_complete            "Your scouting report is ready. Download it now."
type=report_partial             "Your report is ready with some sections incomplete."
type=report_failed_credit_applied
                                "Your report could not be completed. A free report credit has been added to your account."
type=film_error                 "Your film could not be processed: {error_message}. Please re-upload or contact support."
```

Generated by the `notify_coach` Celery task (see AGENTS.md).

**Display:**
- Inline banner-style list at the top of `/dashboard`.
- Each item has View (navigates to the relevant report or team) and Dismiss
  (`POST /notifications/{id}/read`).
- No nav-bar badge, no dropdown — the UI is a simple inline list. Earlier doc revisions
  described a nav-bar component that was never built.

**Backend:**
- `GET /notifications/` returns the 50 most recent notifications. The frontend filters
  unread client-side.
- `POST /notifications/read-all` is implemented but no UI calls it today.

---

## FLOW 10 — ADMIN (`/admin`) — IS_ADMIN ONLY

**Access gate:** Every admin route checks `is_admin` via live DB query on every request
(`services/clerk.py::require_admin`). The frontend `admin/layout.tsx` probes `/admin/users`
on mount; a 403 response renders an "Access denied." page.

### Admin home — `/admin` IS the Corrections page

`/admin/page.tsx` IS the corrections page. The admin nav labels `/admin` as "Corrections."
There is **no separate `/admin/corrections` URL** and no `/admin` summary-stats home.

**Corrections page UX (as currently built):**
- Recent corrections list with filter (prompt version, section type).
- "New Correction" form: manual entry of `report_id`, `film_id`, `ai_claim`, `category`,
  `confidence`, `prompt_version`, `admin_notes`, `is_correct`, `correct_claim`.
- Submit → `POST /admin/corrections`.

This is **not** the per-claim quick-review UX that earlier doc revisions described
(click claim → ✓/✗ → optional correction). The shipped UX is manual form entry.

### Pattern Analyzer — `/admin/patterns`

- Filter: `prompt_version` only (no date-range filter today).
- Tables: by-category error rate, by-section error rate.
- No "Refresh" button, no Gemini-generated recommendation text — those were spec'd but
  never wired.

### User Management — `/admin/users`

- Table columns: email, reports used, credits, joined date.
- "Add Credits" button per row → number input → `POST /admin/users/{user_id}/credits`.
- No "last active" column (would require Datadog/PostHog data; deferred to Issue #29).

### Dead Letters — not built

There is no `/admin/dead-letters` page. Dead-letter rows exist in Neon
(`dead_letter_tasks` table) but no admin UI surfaces them. Manual replay is via DB query
+ direct Celery call. UI build-out is future Phase 5 work.

---

## GLOBAL UI RULES

**Colors (from Tailwind theme — see STACK.md):**
- Background: `#0a0a0a`
- Surface: `#141414`
- Accent: `#F97316` (orange)
- Border: `#262626`
- Dark theme throughout. No light mode.

**Loading states:**
- Every API call shows a loading indicator on the triggering element.
- Never show a blank screen while data loads.

**Error handling:**
- Every API error surfaces a message to the coach. No silent failures.
- Errors appear inline near the action that caused them.
- Full-page errors (team not found, dashboard load failure) show a simple error page with
  a Retry button and a "Go to Dashboard" link.

**Responsive:**
- Responsive web. No mobile app.
- Target: functional on tablet (coaches use iPads on the sideline).
- Minimum supported width: 768px.

**Polling:**
- Only two surfaces actively poll: the team page (Films tab — every 10s while any film is
  non-terminal) and the report detail page (`/reports/[id]` — every 10s while non-terminal).
- All other screens are static.

---

*Last updated: 2026-05-19 — Full rewrite for synthesis-only mode (D-024). Route map*
*aligned to disk. Single-PUT upload flow (multipart removed). Stripe redirect URLs and*
*endpoint names corrected. Admin section rewritten to match shipped UX. Per-section*
*model_used + generation_time, partial/pending states, Retry Film button, dev seed*
*endpoint, JWT refresh on long uploads, no-team-selected state, and recent-films list*
*all documented. Notifications display matches shipped inline banner (no nav-bar*
*dropdown). No graceful synthesis degradation language (D-025). process_film timeout*
*at 120 min (D-026).*
*Flow documentation version: v2.0.0*
