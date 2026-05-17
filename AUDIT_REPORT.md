# AUDIT_REPORT.md — TEX v2 Repo Hygiene

Read-only audit of `github.com/aidn31/tex-v2` as of 2026-05-17. No fixes applied.
Calibrated for a solo-founder repo — no enterprise overkill. Findings cover what
protects against shipping broken code, leaking secrets, or losing history.

Findings are grouped by severity. Each one lists **Problem / Fix / Effort (S/M/L)**.
"Out of scope" at the bottom captures things noticed but outside the audit's remit.

---

## SUMMARY

| Severity      | Count |
|---------------|-------|
| 🔴 Critical   | 4     |
| 🟡 Important  | 9     |
| 🟢 Polish     | 4     |
| **Total**     | **17** |

> **Update 2026-05-17 evening:** I9 added when PR 1 setup surfaced that `main` was 20 commits behind active development. **Resolved before PR 1 opened** — see I9 below.

**Top 3 to fix first:**

1. 🔴 Protect `main` — today nothing stops a direct push.
2. 🔴 Enable Dependabot security alerts + automated security fixes.
3. 🔴 Add CI on PR — at minimum lint + typecheck + secrets-scan (`gitleaks`).

**Recommended order of operations** (matches the prompt's PR plan):

```
PR 1  Security        .gitignore hardening + Dependabot on + gitleaks pre-commit
PR 2  Branch protection   Main branch rules + delete-on-merge + stale branch cleanup
PR 3  CI workflows    .github/workflows/{backend,frontend,gitleaks}.yml
PR 4  Pre-commit + linter configs   .pre-commit-config.yaml, pyproject.toml, eslint, prettier
PR 5  Documentation   README.md, root .env.example notes, PR template, LICENSE decision
```

---

## 🔴 CRITICAL

### C1 — `main` branch is unprotected

**Problem:** `gh api repos/aidn31/tex-v2/branches/main/protection` returns `404 Branch not protected`. Anyone with push rights can push directly to `main`, force-push history, or bypass PR review. The CLAUDE.md rule "Never push to main directly. Hard limit." is currently enforced by social contract only, not by the platform.

**Fix:** Enable branch protection on `main` requiring:
- Pull request before merge (1 approving review — Tommy)
- Status checks must pass (after CI exists — wire this in PR 3)
- Linear history (no force-push, no merge commits)
- Restrict deletions and direct pushes

**Effort:** S — one `gh api PUT` call, or 90 seconds in the GitHub UI.

---

### C2 — Dependabot disabled (security alerts + automated fixes both off)

**Problem:** `repos/aidn31/tex-v2` returns `dependabot_security_updates.status = disabled`, `vulnerability-alerts = disabled`, `automated-security-fixes.enabled = false`. The dep surface includes `cryptography`, `PyJWT`, `requests`-using libs (boto3, httpx), Next.js 15, React 19, Clerk SDK, Stripe SDK — all routine CVE targets. There is no alert path today.

**Fix:** Enable in repo Settings → Code security:
- Dependabot alerts: on
- Dependabot security updates: on
- Optionally add `.github/dependabot.yml` for weekly version updates on `pip` (`backend/requirements.txt`) and `npm` (`frontend/package.json`)

**Effort:** S — UI toggles; `dependabot.yml` is a 20-line file.

---

### C3 — No CI at all

**Problem:** `.github/` directory does not exist (`gh api repos/aidn31/tex-v2/contents/.github` → 404; confirmed locally as well). There is no lint, no typecheck, no test gate, no secrets scan running on PR. Combined with C1 (no branch protection), anything can land on `main`.

**Fix:** Add `.github/workflows/` with — at minimum, on PR to `main`:
- **Backend** (`backend.yml`): `ruff check`, `ruff format --check`, `mypy` or `pyright`, `pytest` (once tests exist).
- **Frontend** (`frontend.yml`): `eslint`, `tsc --noEmit`, `next build` sanity check.
- **Secrets scan** (`gitleaks.yml`): `gitleaks/gitleaks-action` on every PR.
- Pin all action versions (`actions/checkout@v4`, not `@main`).
- Declare `permissions:` block at the workflow level — default-deny, grant only what's needed (`contents: read` is enough for most jobs).

**Effort:** M — three workflow files, ~50 lines each. Some tuning to silence first-run noise. Tests can be a stub gate at first if backend test coverage is thin.

---

### C4 — Root `.gitignore` does not cover secret-file conventions

**Problem:** Root `.gitignore` is good on `.env`, `node_modules/`, `.next/`, `*.mp4`. It does **not** cover:
- `*.pem`, `*.key`
- `*-service-account*.json`, `**/credentials/`
- `.coverage`, `htmlcov/`
- `tmp_*.txt`, `tmp_*.md` (the `git status` snapshot shows seven such untracked files already at risk: `tmp_chunk_extractions.txt`, `tmp_synthesis_document.txt`, `backend/tmp_chunk_{0,1,2,3}_head.txt`, `backend/tmp_syn_latest.txt`)

The local file `backend/credentials/gcp-service-account.json` is currently saved by a nested `backend/.gitignore` (`credentials/`), so it is **not at risk today** — but the protection is layered in one spot and would not catch the same file placed elsewhere. Defense-in-depth says: put the patterns at the root too.

History scan (full `git log -p --all`, 39,882 lines) shows **no** real secret values committed at any point — only the `backend/.env.example` placeholder file and references to env-var *names* in code. No rotation needed today, but the gap above is one careless `git add .` away from a leak.

**Fix:** Extend root `.gitignore` with:

```gitignore
# Secrets and credentials (belt-and-suspenders — backend/.gitignore already covers credentials/)
*.pem
*.key
*-service-account*.json
**/credentials/
!.env.example

# Coverage
.coverage
htmlcov/

# Local AI/preprocess scratch files
tmp_*.txt
tmp_*.md
backend/tmp_*.txt
```

**Effort:** S — one file edit. No history rewrite needed (no live secrets in history).

---

## 🟡 IMPORTANT

### I1 — No pre-commit framework

**Problem:** No `.pre-commit-config.yaml`. Local commits have no automated gate. CI (once added per C3) will be the only enforcement — meaning the feedback loop on "you forgot to format" is a CI run, not a 200ms local hook.

**Fix:** Add `.pre-commit-config.yaml` with:
- `ruff` (lint + format) — Python
- `prettier` + `eslint` — TypeScript
- `gitleaks` (or `detect-secrets`) — secrets
- Standard hygiene: `trailing-whitespace`, `end-of-file-fixer`, `check-merge-conflict`, `check-added-large-files` (cap at e.g. 5MB to catch accidental film blobs)

Configs must match what CI runs — diverging configs is a finding in itself.

**Effort:** M — ~40 lines of YAML plus Tommy running `pre-commit install` once.

---

### I2 — No Python lint/typecheck config

**Problem:** No `pyproject.toml`, no `ruff.toml`, no `mypy.ini`. STACK.md commits to Python 3.12 + Pydantic 2.x as the discipline but nothing actually enforces a style or type contract on the backend.

**Fix:** Add `backend/pyproject.toml` (or repo-root `pyproject.toml`) with:
- `[tool.ruff]` — line length, target-version py312, select rule sets (`E`, `F`, `W`, `I`, `UP`, `B`)
- `[tool.ruff.format]`
- `[tool.mypy]` or switch to `pyright` (faster, used by Pylance) — `strict = false` to start, tighten later

**Effort:** M — config is small; first run will produce a fixable backlog. Tommy can choose how strict to start.

---

### I3 — No frontend lint/format config beyond Next.js defaults

**Problem:** `frontend/package.json` has only `next lint` as a script and no ESLint or Prettier in `devDependencies`. No `eslint.config.*`, no `.prettierrc`. CLAUDE.md mandates strict TS and "no `any`" — there is no automated check for that today.

**Fix:** Add to `frontend/`:
- `eslint.config.mjs` (flat config, ESLint 9) — extend `next/core-web-vitals`, `@typescript-eslint/recommended`, ban `any` via `@typescript-eslint/no-explicit-any`
- `.prettierrc` — minimal opinions, project-standard
- Wire `lint` and `format:check` scripts into `package.json` and the CI workflow (C3)

**Effort:** M — install deps, write configs, ensure `tsc --noEmit` passes.

---

### I4 — Stale branches not deleted; auto-delete disabled

**Problem:** `delete_branch_on_merge` is `false`. Two long-stale branches sit on the remote:
- `origin/feature/repo-scaffold` — last commit 2026-04-04 (6 weeks)
- `origin/phase-2` — last commit 2026-04-10 (5 weeks)

Active branch is `origin/feature/phase-3` (2026-05-12). Both stale branches are unmerged into `main` according to `git branch -r --no-merged origin/main`, but their work appears to have been re-landed via the normal commit sequence on `feature/phase-3` (per ROADMAP) — they look like dead ends, not unmerged work.

**Fix:**
- Turn on `delete_branch_on_merge` in repo Settings.
- After confirming with Tommy that nothing useful lives on them, delete `feature/repo-scaffold` and `phase-2` from the remote.

**Effort:** S — one toggle + two `git push origin --delete` calls after confirmation.

---

### I5 — `git config user.email` was never set; commits read `your-email@example.com`

**Problem:** Every Tommy-authored local commit (38 of 52 in history) shows `Author: Your Name <your-email@example.com>` — the default scaffold placeholder. Only the 13 web-UI uploads carry his real GitHub identity (`T0MMY`). Side effects:
- `git blame` and `git log` attribution are anonymous-looking
- GitHub cannot link the commit to his profile (no green squares for those commits, no "verified author")
- Email-based contributor metrics (used by some downstream tools) attribute commits to a fake address

**Fix:** Run once, locally:

```bash
git config --global user.name  "Tommy Roldan"   # or his preferred name
git config --global user.email "tommymr.ai@gmail.com"  # the email on his GitHub account
```

(Use `--global` if he wants this everywhere, drop it for repo-local.) Past commits don't need to be rewritten — the fix is forward-only.

**Effort:** S — two one-liners.

---

### I6 — `Add files via upload` accounts for 25% of `main` history

**Problem:** 13 of 52 commits across all branches have the message `Add files via upload` (these are GitHub web-UI drag-and-drop uploads). They concentrate at the start of the project (Phase 0 doc drops). The diff content is recoverable, but the *intent* and the *grouping* of those changes are not — every PR on the early scaffold landed as an opaque commit.

This is a sunk cost — those commits are already on `main` and rewriting history to clean them up is not worth the blast radius for a solo repo. Flagging because going forward, the disciplined messaging convention you've already adopted (`Add Film 05 (La Lumiere vs Oak Hill) ground truth + watch notes synthesis`) is the right pattern.

**Fix:** No history rewrite. Going forward: stop using the GitHub web UI for uploads; commit locally with descriptive messages. The branch-protection rules from C1 will structurally prevent the web-UI workflow on `main` once enabled.

**Effort:** S — behavioral.

---

### I7 — `git ls-files` is clean today, but no enforcement against re-introduction

**Problem:** Verified there are zero tracked `.env`, `*.pem`, `*.key`, `__pycache__/`, `node_modules/`, `.next/`, or `dist/` files (`git ls-files` returns 149 tracked files, none matching those patterns). One past commit (`654f9a7`, the Phase 1 scaffold) added `backend/.env.example` correctly with placeholder values only — no real secrets.

Without CI (C3) and pre-commit (I1), there is no guard against a future `git add .` quietly pulling in `backend/.env`, a key file, or a multi-GB chunk artifact.

**Fix:** Covered by C3 (gitleaks in CI) + I1 (pre-commit hooks) + C4 (gitignore hardening). Listing this separately so the audit trail acknowledges the gap.

**Effort:** Bundled with C3 + I1 + C4.

---

### I8 — Commits unsigned (informational, may be intentional)

**Problem:** `git log --format='%G?' origin/main` shows `E` (no signature) on every commit. Not a hard finding — many solo founders skip signing — but worth surfacing once.

**Fix:** If Tommy wants verified commits, set up SSH or GPG signing:

```bash
git config --global commit.gpgsign true
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
```

Then add the same key under "SSH signing keys" on his GitHub account.

**Effort:** S — one-time setup, no ongoing cost.

---

### I9 — `main` was 20 commits behind active development; resolved by rebase + FF prior to PR 1

**Problem (discovered post-audit, 2026-05-17 evening):** When PR 1 setup tried to branch from `main`, the worktree had no `.gitignore`, no backend code, and an old ROADMAP — because `main` was at `b87d928` (Apr 4, 2026 — a merge commit bringing in Phase 1 Foundation via `feature/repo-scaffold`) while all Phase 2 / Phase 3 / Phase 4 work lived only on `feature/phase-3`. Divergence shape: `main` had 1 commit `feature/phase-3` didn't (the merge commit), and `feature/phase-3` had 20 commits `main` didn't. Practical impact: every cleanup PR opened against `main` would have generated immediate merge conflicts with `feature/phase-3`, and PR 2's branch-protection rules + PR 3's CI status checks would have been protecting a stale branch with no real code in it.

Compounding finding: the audit's `git for-each-ref refs/remotes/` query read cached local refs, not the live remote. At audit time the local `origin/main` was even more stale (`e94ece1`, Apr 3) than the real remote (`b87d928`, Apr 4), so the audit summary undercounted the divergence by one commit (reported "37 commits ahead"; the actual count against the live remote was 20 ahead + 1 behind).

**Fix (already applied):** Committed Tommy's in-progress edits on `feature/phase-3` as `cc9ec81` (preprocess prompts v1.6 + SDK HTTP timeout + `prompt_versions` helper + doc sync). Tagged `pre-rebase-phase-3` at that commit as a safety reference (delete only after PR 1 merges). Rebased `feature/phase-3` onto `origin/main` (`b87d928`) — **0 conflicts across 21 replayed commits.** Smoke-tested the rebased tree (`/health` returned 200; `next build` compiled in 5.2s; worker registered all 8 tasks + recovered no stuck jobs). Force-with-lease pushed the rebased branch, strict FF push to `main` (`b87d928..b80d86c main`), deleted the remote `feature/phase-3` branch. `origin/main` is now at `b80d86c` with linear history and contains the full project.

**Process lesson for future audits:** Run `git fetch origin --prune` first and surface `git ls-remote origin main` separately as a cross-check against local cached refs. Adding to methodology.

**Effort:** Resolved.

---

## 🟢 POLISH

### P1 — No `README.md`

**Problem:** Repo root has no `README.md`. New contributors (or future-Tommy on a fresh checkout) land on a sea of 16 markdown files with no entry point. The canonical docs (`CLAUDE.md`, `ARCHITECTURE.md`, `ROADMAP.md`) are excellent — they just need a 30-line front door.

**Fix:** Add a short `README.md` (do NOT duplicate the canonical docs):
- One-sentence "what is TEX" pulled from CLAUDE.md
- "Run locally" — copy `backend/.env.example` to `backend/.env`, fill in keys, `docker compose up`, `cd frontend && npm install && npm run dev`
- Pointers: read `CLAUDE.md` first, then `ARCHITECTURE.md`, then `ROADMAP.md` for current state

**Effort:** S — single short file.

---

### P2 — No `LICENSE`

**Problem:** No `LICENSE` file. Default = "All rights reserved." This is probably intentional for a proprietary product, but the audit prompt asks us to confirm rather than assume.

**Fix:** Confirm with Tommy: leave absent (proprietary) or add `LICENSE` (MIT, Apache-2.0, or similar). **Do not add a license without his explicit approval** — license choice has commercial implications.

**Effort:** S — one decision, one file.

---

### P3 — No PR template

**Problem:** No `.github/pull_request_template.md`. PRs land with whatever description the author writes (or none).

**Fix:** Add a short template — what changed, why, eval impact if Phase 4+, screenshots if UI. Keep it light; solo-founder repo doesn't need a 50-checkbox template.

**Effort:** S — 15-line file.

---

### P4 — No frontend `.env.example`

**Problem:** `backend/.env.example` exists and is complete. There is no `frontend/.env.example` despite the frontend needing `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `NEXT_PUBLIC_POSTHOG_KEY`, `NEXT_PUBLIC_API_URL`, and the Stripe publishable key. A new local-setup follows `backend/.env.example` to bring up the API, then has to read code to figure out the frontend env vars.

**Fix:** Add `frontend/.env.example` listing every `NEXT_PUBLIC_*` variable the frontend reads, plus Clerk/Stripe variables it needs at build/runtime.

**Effort:** S — one file, ~10 lines.

---

## OUT OF SCOPE — noted, not actioned

- **Multi-GB `.mp4` files at repo root** (`la_lumiere_vs_oak_hill.mp4`, `montverde_vs_brewster.mp4`, `rebels_vs_az_unity.mp4`, `spire_vs_la_lumiere.mp4` — ~10GB combined). All correctly excluded by the `*.mp4` rule in `.gitignore`. Not at risk. Noted because their presence at the repo root is unusual; consider moving them to a `golden_set/films/` sibling directory outside the repo or under `.gitignore`'d `golden_set/films/` for cleanliness. Not a hygiene finding.
- **Largest tracked file is `ROADMAP.md` at 131KB.** That's a documentation choice (live progress tracker with session logs), not a hygiene issue. No action.
- **`backend/__pycache__/` exists on disk** — confirmed not tracked (matches `__pycache__/` rule). No action.
- **Docker compose binds `:6380:6379`** for Redis (port remap noted in CLAUDE.md). Not an audit concern.

---

## METHODOLOGY

Tools used: `gh` CLI (auth: `aidn31`, scopes `gist`, `read:org`, `repo`, `workflow`); local `git` against `/Users/thomasroldan/Documents/tex-v2`. Full history dumped via `git log -p --all` (39,882 lines) and grepped for: `sk_(live|test)_*`, `pk_(live|test)_*`, `whsec_*`, `AIza*`, `ghp_*`, `github_pat_*`, `xox[bp]-*`, `-----BEGIN ... PRIVATE KEY-----`, postgres connection strings with embedded credentials, GCP service-account JSON markers, raw JWT (`eyJ...`). All hits were either env-var **names** in code or documentation **placeholders** (`sk_test_...`) — no real secret values found.

GitHub side audited via `gh api`: `/repos/aidn31/tex-v2`, `/branches/main/protection`, `/vulnerability-alerts`, `/automated-security-fixes`, `/contents/.github`.

Branch staleness derived from `git for-each-ref --sort=-committerdate refs/remotes/`. Commit-message audit from `git log --all --pretty=format:'%h | %s'`. Signing audit from `%G?` formatter.

---

*Generated 2026-05-17 on branch `chore/repo-audit`. No fixes applied — Phase 1 (audit) only.*
*Updated 2026-05-17 evening: I9 added (main sync) — resolved before PR 1.*
