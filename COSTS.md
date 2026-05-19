# COSTS.md — TEX v2

Per-report cost model. Margin targets. Unit economics under **synthesis-only mode** (D-024).
Every number here is derived from first principles: token counts × API pricing, plus
infrastructure rates. When Gemini pricing changes, update the inputs and re-run the model.

This document is the financial ground truth for every pricing decision TEX makes today.

> **Architecture context.** TEX runs synthesis-only mode (D-024). Prompt 0A processes each
> chunk's video once (Gemini 2.5 Pro). Prompt 0B synthesizes all extractions into a single
> text document (Gemini 2.5 Flash). Sections 1-4 then read that synthesis document as text
> (Gemini 2.5 Pro — no chunk video is replayed). Sections 5-6 build on sections 1-4 text
> (Gemini 2.5 Flash, Claude 3.5 Sonnet fallback). Google's CachedContent API is not used at
> report-generation time — the "cache_uri" passed downstream is a local sentinel encoding
> the text payload. This is the entire cost model below; nothing about it depends on
> Google's caching becoming "viable again."

**Canonical prompt versions: 0A v1.6, 0B v1.6 (see PROMPTS.md) (tracked in Issue #28).**

---

## PRICING INPUTS — VERIFY BEFORE LAUNCH

> ⚠️ **Carry-forward warning.** These rates were last validated in Phase 0 (Q1 2026). They
> have not been re-confirmed against Google AI / Anthropic pricing pages during this rewrite.
> Verify against the current public pricing before any pricing decision based on this model.
> The formulas in this doc are correct; only the rate inputs may be stale.

```
Gemini 2.5 Pro — input, long context (>200K tokens)   $2.50 / 1M tokens
Gemini 2.5 Pro — input, standard (≤200K tokens)       $1.25 / 1M tokens
Gemini 2.5 Pro — output                               $10.00 / 1M tokens
Gemini 2.5 Flash — input                              $0.075 / 1M tokens
Gemini 2.5 Flash — output                             $0.30 / 1M tokens
Claude 3.5 Sonnet — input  (fallback only)            $3.00 / 1M tokens
Claude 3.5 Sonnet — output (fallback only)            $15.00 / 1M tokens

Video token rate (Gemini):                            263 tokens / second of video
```

Source: Google AI pricing page and Anthropic pricing page (Q1 2026 snapshot).
The margin model is only as accurate as these inputs. A 20% Gemini price drop changes
every cost line — re-run the model when pricing shifts materially.

---

## MODEL ASSIGNMENT — WHO RUNS WHAT

```
STAGE                        MODEL              INPUT SHAPE                    CALLS PER REPORT
───────────────────────────────────────────────────────────────────────────────────────────────
Prompt 0A (extract_chunk)    Gemini 2.5 Pro     Chunk video (per chunk)        N (one per chunk)
Prompt 0B (run_chunk_synth)  Gemini 2.5 Flash   Text (all 0A outputs + roster) 1
Section 1 (offensive_sets)   Gemini 2.5 Pro     Text (synthesis_document)      1
Section 2 (defensive_schemes)Gemini 2.5 Pro     Text (synthesis_document)      1
Section 3 (pnr_coverage)     Gemini 2.5 Pro     Text (synthesis_document)      1
Section 4 (player_pages)     Gemini 2.5 Pro     Text (synthesis_document)      1
Section 5 (game_plan)        Gemini 2.5 Flash   Text (sections 1-4)            1 (or Claude on fallback)
Section 6 (adjustments)      Gemini 2.5 Flash   Text (sections 1-5)            1 (or Claude on fallback)
```

Sections 1-4 use Pro on **text input**. Pro is justified here for reasoning quality on
basketball domain language; switching them to Flash is a future eval-harness question, not
a cost-driven decision. Sections 5-6 use Flash because they are simpler text-in/text-out
synthesis where Flash quality is sufficient.

A future Pro→Flash evaluation for sections 1-4 could roughly halve report cost. It's
deliberately out of scope for this cost model — the model documents what TEX runs today.

---

## TOKEN MATH — CANONICAL FILM ASSUMPTIONS

```
Chunk duration:          25 minutes (1,500 seconds) — set by FFmpeg segment_time
Tokens per chunk:        1,500 × 263 = 394,500 tokens ≈ 395K tokens per chunk
Per-chunk context tier:  395K > 200K → Gemini 2.5 Pro long-context rate ($2.50/M)
Prompt 0A output:        ~3,000 tokens (structured observation log per chunk)
Prompt 0B output:        ~6,000 tokens (synthesis document)
Per-section output:      ~2,500 tokens (sections 1-4)
Per-section input  (1-4): ~9,500 tokens (synthesis doc ~6K + roster ~500 + section prompt ~3K)
Per-section input  (5-6): ~12,000 tokens (synthesis + sections 1-4 + section prompt)
Per-section output (5-6): ~2,500 tokens
Roster text:             ~500 tokens (formatted by services/roster_format.py)
```

`N` (chunk count) scales linearly with film duration. We model three durations below.

---

## PROMPT 0A COST — PER CHUNK

```
Per chunk:
  Video input:  395K tokens × $2.50/M   = $0.987
  Output:       3,000 tokens × $10.00/M = $0.030
  ───────────────────────────────────────────────
  Per chunk total                       = $1.02
```

Extractions run in parallel — `N` simultaneous Gemini calls. Wall clock = slowest chunk.
Cost = sum across chunks. This is the dominant Gemini line item for any cold report.

---

## PROMPT 0B COST — SINGLE CALL (Gemini 2.5 Flash, text-only)

```
Input (concatenated 0A outputs + roster):
  4 chunks × 3,000 = 12,000 + 500 roster = 12,500 tokens
  12,500 × $0.075/M                       = $0.0009
Output (synthesis document):
  6,000 tokens × $0.30/M                  = $0.0018
  ────────────────────────────────────────────────
Prompt 0B total                           ≈ $0.003
```

Flash on text is effectively rounding error compared to Prompt 0A. This is the
synthesis-only architecture's economic advantage: 0A pays video tokens once, 0B reduces
that perception output to a small text document, and sections 1-4 then read text only.

---

## SECTIONS 1-4 COST — Gemini 2.5 Pro, text input from synthesis document

```
Per section call:
  Input:  9,500 tokens × $1.25/M (≤200K standard tier) = $0.012
  Output: 2,500 tokens × $10.00/M                       = $0.025
  ──────────────────────────────────────────────────────────────
  Per section total                                     = $0.037

4 sections in parallel via Celery chord:
  4 × $0.037                                            = $0.149
```

Pro is used here (not Flash) for reasoning quality — basketball domain language and
scouting-vocabulary discipline. The Pro premium on **text input** is small (~10× Flash on
inputs, but inputs are tiny) and the output budget is the same regardless of input model.
Total Pro cost for sections 1-4 ≈ $0.15.

The section-cache short-circuit (PR #32 ARCH update) writes these four outputs to
`film_analysis_cache.sections` after they complete. A subsequent report against the same
film at the same composite `prompt_version` reads them directly — sections 1-4 cost drops
to **$0** on regeneration.

---

## SECTIONS 5-6 COST — Gemini 2.5 Flash, text input from sections 1-4

```
Per section call:
  Input:  12,000 tokens × $0.075/M = $0.0009
  Output: 2,500 tokens × $0.30/M   = $0.00075
  ────────────────────────────────────────────
  Per section total                ≈ $0.002

2 sections (sequential — section 6 depends on section 5):
  2 × $0.002                       ≈ $0.004
```

Sections 5-6 are not cached at the section level — their content depends on coach intent
and may carry roster-specific framing in the future. Every report pays $0.004 here.

### Worst-case fallback — Claude 3.5 Sonnet on both sections

```
Per section call:
  Input:  12,000 tokens × $3.00/M  = $0.036
  Output: 2,500 tokens × $15.00/M  = $0.038
  ────────────────────────────────────────────
  Per section total                = $0.074

Both sections via Claude (Flash unavailable):
  2 × $0.074                       = $0.148
```

Worst-case adds $0.144 above the Flash baseline. Fallback monitoring is currently absent
(see Issue #27 for the `fallback_events` table fate); operationally, a sustained Flash
outage triggering both fallbacks on every report is the worst case modeled here.

---

## INFRASTRUCTURE PER REPORT (carry-forward)

```
Cloud Run compute:
  tex-worker-film     ~20 min × 4 vCPU × $0.00002/vCPU-sec  = $0.096
  tex-worker-report   ~5 min  × 1 vCPU × $0.00002/vCPU-sec  = $0.006
  tex-worker-section  ~10 min × 4 vCPU × $0.00002/vCPU-sec  = $0.048
  tex-api             allocated across reports               = ~$0.01
  ──────────────────────────────────────────────────────────────────
  Compute total                                              ≈ $0.16

Cloudflare R2 (amortized):
  Raw film + PDF storage + class A/B operations              ~$0.02

Neon Postgres + Redis (amortized at early volume)            ~$0.03

Sentry / Datadog (currently unwired — see Issue #29)         $0 today
  Phase 5 estimate when wired (amortized at early volume)    ~$0.05

Infrastructure total                                         ≈ $0.21 today
                                                             ≈ $0.26 once Issue #29 is closed
```

Empirical note (CLAUDE.md): FFmpeg compression in Docker for Mac runs ~10× slower than
native, and observed `process_film` runtimes on real 2-hour film hit 40+ minutes for
compression alone. The 20-minute compute estimate above is a Cloud Run-native target,
not the Docker dev runtime. If production Cloud Run latency lands closer to Docker dev,
revise the compute line upward — but the compute share of total cost is small enough that
even a 3× compute overrun doesn't materially affect the margin model.

---

## PER-REPORT COST — THREE FILM SCENARIOS

### Scenario A — 1-hour film (3 chunks)

```
COMPONENT                            COLD          REGEN (sections cached)
──────────────────────────────────────────────────────────────────────────
Prompt 0A (3 × $1.02)                 $3.06         $0       (synthesis cached)
Prompt 0B (1 × Flash)                 $0.003        $0       (synthesis cached)
Sections 1-4 (4 × Pro on text)        $0.149        $0       (sections cached)
Sections 5-6 (Flash)                  $0.004        $0.004
Infrastructure                        $0.21         $0.05    (only 5-6 workers run)
──────────────────────────────────────────────────────────────────────────
TOTAL (Flash primary)                 $3.43         $0.054
TOTAL (Claude fallback both 5-6)      $3.57         $0.198
```

### Scenario B — 2-hour film (4 chunks) — baseline

```
COMPONENT                            COLD          REGEN (sections cached)
──────────────────────────────────────────────────────────────────────────
Prompt 0A (4 × $1.02)                 $4.08         $0
Prompt 0B (1 × Flash)                 $0.003        $0
Sections 1-4 (4 × Pro on text)        $0.149        $0
Sections 5-6 (Flash)                  $0.004        $0.004
Infrastructure                        $0.21         $0.05
──────────────────────────────────────────────────────────────────────────
TOTAL (Flash primary)                 $4.45         $0.054
TOTAL (Claude fallback both 5-6)      $4.59         $0.198
```

### Scenario C — 3-hour film (7 chunks)

```
COMPONENT                            COLD          REGEN (sections cached)
──────────────────────────────────────────────────────────────────────────
Prompt 0A (7 × $1.02)                 $7.14         $0
Prompt 0B (1 × Flash)                 $0.003        $0
Sections 1-4 (4 × Pro on text)        $0.149        $0
Sections 5-6 (Flash)                  $0.004        $0.004
Infrastructure                        $0.21         $0.05
──────────────────────────────────────────────────────────────────────────
TOTAL (Flash primary)                 $7.51         $0.054
TOTAL (Claude fallback both 5-6)      $7.65         $0.198
```

Prompt 0A scales linearly with chunk count. Everything downstream of synthesis is
chunk-count-independent.

---

## TWO-LAYER CACHING — WHY MOST REPORTS COST CENTS, NOT DOLLARS

TEX's `film_analysis_cache` table is keyed on `(file_hash, composite_prompt_version)` and
holds two reusable artifacts:

1. **`synthesis_document`** (Layer 1) — Prompt 0A + Prompt 0B output. Written once per
   film. Every subsequent report on the same film at the same preprocess prompt version
   skips Phase A entirely.
2. **`sections` jsonb** (Layer 2) — Sections 1-4 outputs. Written after a successful
   report assembles. Every subsequent **single-film** report at the same composite prompt
   version skips the section-generation chord entirely.

```
SCENARIO                                COST (2-hour film, Flash primary)
─────────────────────────────────────────────────────────────────────────
Cold report — never-seen film            $4.45
Re-upload — same film hash, no section cache yet
  (Phase A cached, sections 1-4 fresh)   $0.36
Regen — same film, same prompt version
  (Phase A cached, sections 1-4 cached)  $0.054
```

The "re-upload" row is what happens when a second coach uploads the same opponent's film.
Layer 1 fires for them at no Gemini cost. Layer 2 fires for them once their own report
finishes — but every subsequent regen of *their* report against that film is then ~$0.05.

At scale with many coaches scouting the same EYBL programs, Layer 1 hit rate is the
dominant lever on blended unit cost. Layer 2 hit rate drives the regen-vs-fresh-report
margin for any individual coach.

---

## STARTER TIER MARGIN

STARTER is the only wired pricing tier (Issue #30 tracks future tier add-back). Pay-per-report.

```
List price:                                  $49.00
Stripe processing fee (2.9% + $0.30):        $1.72
Net revenue per report:                      $47.28
```

### Cold report margin (worst plausible per-report cost)

| Scenario | Cost | Gross margin | Margin % |
|---|---:|---:|---:|
| 1-hour film, Flash primary | $3.43 | $43.85 | 92.7% |
| 2-hour film, Flash primary | $4.45 | $42.83 | 90.6% |
| 3-hour film, Flash primary | $7.51 | $39.77 | 84.1% |
| 2-hour film, Claude fallback both 5-6 | $4.59 | $42.69 | 90.3% |
| 3-hour film, Claude fallback both 5-6 | $7.65 | $39.63 | 83.8% |

### Regenerated report (sections cached)

| Scenario | Cost | Gross margin | Margin % |
|---|---:|---:|---:|
| Any film size, Flash primary | $0.054 | $47.23 | 99.9% |
| Any film size, Claude fallback both 5-6 | $0.198 | $47.08 | 99.6% |

A first paying coach on a 3-hour film at Flash primary nets ~$40 gross. Subsequent regens
of that same report net ~$47 gross. Subsequent first-paying coaches on the same film hash
net ~$47 minus the section-generation-only run (~$0.36) = ~$46.92 gross.

These are gross margin figures — they do not account for fixed monthly infrastructure
(see "Fixed costs" below) or for cost lines deferred until Issue #29 closes.

### Margin floor

If pricing inputs at the top of this doc are off by 2× on Pro long-context (a meaningful
miss), the 3-hour cold report cost rises from $7.51 to ~$14.65 — still 69% margin on STARTER.
The synthesis-only architecture is robust to pricing surprises in a way the prior
caching-dependent model was not.

---

## FAILED REPORT — FAILURE CREDIT IMPACT

Per D-017, a technical failure after payment applies a free credit to the coach's account.
The coach re-runs at no additional cost. TEX has paid the original Gemini and infrastructure
cost; the re-run pays again.

```
2-hour film example, cold report fails after sections 1-4 partially complete:
  Original cost (sunk):                    $4.45
  Re-run cost (synthesis cached, sections rerun):  $0.36
  ─────────────────────────────────────────────────────
  Total cost across original + re-run:     $4.81
  Revenue (single $49 payment):            $47.28
  Gross margin after failure + credit:     $42.47 (89.8%)
```

A single failure does not invert margin. A coach experiencing systematic failures would
trigger an operational alert (Phase 5 — Issue #29) before per-report margin is impacted.

---

## FIXED COSTS — MONTHLY

These costs exist regardless of report volume. At low volume they dominate. At high volume
they amortize.

```
PROVIDER          SERVICE                       COST/MONTH    NOTES
──────────────────────────────────────────────────────────────────────────────
Google Cloud Run  tex-api (min 1)               ~$20          1 vCPU, 2Gi, always on
                  Workers (scale to 0)          $0–50         pay only when running
Neon              PostgreSQL                    $0–19         free tier until 10GB
Redis             Upstash serverless            $0–10         pay-per-request at low volume
Cloudflare R2     Storage                       $5–20         depends on film retention
Vercel            Frontend                      $0–20         free tier sufficient at launch
Clerk             Auth                          $0–25         free tier to 10K MAU
Stripe            Payments                      2.9% + $0.30  per transaction only
Sentry            Error tracking (Issue #29)    $0            unwired; free tier when wired
Datadog           APM (Issue #29)               $0            unwired; ~$15+/month when wired

Estimated fixed costs at launch:                ~$50–125/month
Breakeven on fixed costs (STARTER at $49):      2–3 reports/month
```

Fixed costs are not a concern at launch. A single paying coach covers them. Variable Gemini
costs are covered by per-report margin per the scenarios above.

---

## CACHE HIT RATE — STRATEGIC LEVER

Cache hit rate is the dominant lever on blended unit cost. It improves automatically with
usage as more coaches scout overlapping opponents.

```
ASSUMPTION                                            CACHE HIT %    BLENDED COST
                                                                     (2-hour film,
                                                                     STARTER pricing)
──────────────────────────────────────────────────────────────────────────────────
Month 1 — 10 coaches                                  ~5%            $4.27
Month 3 — 50 coaches                                  ~20%           $3.62
Month 6 — 150 coaches                                 ~40%           $2.83
Month 12 — 500 coaches, popular EYBL programs hit     ~60%           $2.05
```

At month 12 with 60% cache hit, blended cost per 2-hour report is ~$2.05 → ~96% gross
margin. This is the compounding moat in dollar terms: every coach added increases the
hit rate for every subsequent coach. Synergy and human-scout competitors cannot match this
unit economics shape without an equivalent installed base.

---

## WHEN TO RE-RUN THIS MODEL

Update the pricing inputs at the top of this document first, then recalculate from there.
The formulas do not change. Only the inputs do.

Trigger re-runs when any of the following change:

1. Gemini pricing changes (check monthly — historically dropping).
2. Gemini 2.5 Pro or Flash is replaced with a new model version.
3. The Pro→Flash evaluation for sections 1-4 produces a switch decision.
4. Average film duration deviates from the 2-hour baseline.
5. Prompt 0A or 0B output token count changes materially (prompt revision changes length).
6. Cache hit rate crosses a 10-point threshold (e.g. 10% → 20%).
7. Infrastructure provider pricing changes.

Pricing tier changes (e.g. Coach / Program tiers per Issue #30) require a new section in
this document, not edits to STARTER.

---

*Last updated: 2026-05-19 — Full rewrite for synthesis-only mode (D-024). Three-scenario*
*per-report cost model. Section-cache short-circuit modeled. Subscription tiers stripped*
*pending Issue #30. Batch API routing stripped (not built). Pricing inputs flagged as*
*Q1 2026 carry-forward — verify before launch.*
*Cost model version: v2.0.0*
