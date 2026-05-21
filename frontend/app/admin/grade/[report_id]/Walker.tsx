'use client';

import {
  Dispatch,
  useCallback,
  useEffect,
  useReducer,
  useRef,
  useState,
} from 'react';
import { AdminReportSection } from '@/lib/api';
import { SECTION_ORDER, sectionLabel, sectionOrderIndex } from '@/lib/grading/sections';
import { Claim, splitClaims } from '@/lib/grading/splitClaims';

// Status values that map 1:1 to the corrections.claim_status enum
// (captured/missed/hallucinated). 'skipped' and null are client-only —
// R3+R10 filters those out before writing.
export type ClaimStatus = 'captured' | 'missed' | 'hallucinated' | 'skipped' | null;

export type Classifications = Record<string, Exclude<ClaimStatus, null>>;

export type WalkerAction =
  | { type: 'classify'; status: Exclude<ClaimStatus, null> }
  | { type: 'advance' }
  | { type: 'back' }
  | { type: 'forward' }
  | { type: 'undo' }
  | { type: 'acknowledgeSectionTransition' };

export type WalkerState = {
  cursor: number;
  classifications: Classifications;
  history: string[];
  sectionTransitionPending: boolean;
};

// R3+R10: parent owns persistence. Walker fires this when a classification
// happens; saves are fire-and-forget so a slow network never blocks the
// session. Parent tracks pending retries and surfaces failures.
export type SaveClassificationFn = (
  claim: Claim,
  status: 'captured' | 'missed' | 'hallucinated',
  correctClaim: string | null,
) => void;

export const INITIAL_WALKER_STATE: WalkerState = {
  cursor: 0,
  classifications: {},
  history: [],
  sectionTransitionPending: false,
};

export function buildSortedClaims(sections: AdminReportSection[]): Claim[] {
  const ordered = [...sections].sort(
    (a, b) => sectionOrderIndex(a.section_type) - sectionOrderIndex(b.section_type),
  );
  const out: Claim[] = [];
  for (const s of ordered) {
    if (s.status !== 'complete' || !s.content) continue;
    out.push(...splitClaims(s.section_type, s.content));
  }
  return out;
}

function isSectionBoundary(claims: Claim[], from: number, to: number): boolean {
  if (to >= claims.length || from < 0 || from >= claims.length) return false;
  return claims[from].section_type !== claims[to].section_type;
}

// Exposed for use from the parent page (state must survive mode toggles).
export function useWalkerReducer(
  claims: Claim[],
): [WalkerState, Dispatch<WalkerAction>] {
  const reducer = useCallback(
    (state: WalkerState, action: WalkerAction): WalkerState => {
      switch (action.type) {
        case 'classify': {
          if (state.cursor >= claims.length) return state;
          if (state.sectionTransitionPending) return state;
          const current = claims[state.cursor];
          const nextCursor = state.cursor + 1;
          const crossing = isSectionBoundary(claims, state.cursor, nextCursor);
          return {
            cursor: nextCursor,
            classifications: { ...state.classifications, [current.id]: action.status },
            history: [...state.history, current.id],
            sectionTransitionPending: crossing,
          };
        }
        case 'advance': {
          if (state.cursor >= claims.length) return state;
          if (state.sectionTransitionPending) return state;
          const nextCursor = state.cursor + 1;
          const crossing = isSectionBoundary(claims, state.cursor, nextCursor);
          return {
            ...state,
            cursor: nextCursor,
            sectionTransitionPending: crossing,
          };
        }
        case 'back': {
          if (state.cursor === 0) return state;
          return {
            ...state,
            cursor: state.cursor - 1,
            sectionTransitionPending: false,
          };
        }
        case 'forward': {
          if (state.cursor >= claims.length) return state;
          if (state.sectionTransitionPending) return state;
          const nextCursor = state.cursor + 1;
          const crossing = isSectionBoundary(claims, state.cursor, nextCursor);
          return {
            ...state,
            cursor: nextCursor,
            sectionTransitionPending: crossing,
          };
        }
        case 'undo': {
          // R3+R10 Path A: undo is UI-local only. The corresponding DB row
          // (if one was written) stays put — corrections are append-only by
          // design. If the grader re-classifies, a NEW row is written and
          // the latest by created_at per (report_id, ai_claim, section_type)
          // is authoritative. This keeps the audit trail intact and avoids
          // needing a DELETE endpoint.
          if (state.history.length === 0) return state;
          const lastId = state.history[state.history.length - 1];
          const targetIndex = claims.findIndex((c) => c.id === lastId);
          if (targetIndex === -1) return state;
          const { [lastId]: _removed, ...rest } = state.classifications;
          void _removed;
          return {
            cursor: targetIndex,
            classifications: rest,
            history: state.history.slice(0, -1),
            sectionTransitionPending: false,
          };
        }
        case 'acknowledgeSectionTransition': {
          return { ...state, sectionTransitionPending: false };
        }
        default:
          return state;
      }
    },
    [claims],
  );

  return useReducer(reducer, INITIAL_WALKER_STATE);
}

export default function Walker({
  claims,
  state,
  dispatch,
  onExit,
  onSaveClassification,
  saveErrorCount,
  pendingRetryCount,
  savedCount,
}: {
  claims: Claim[];
  state: WalkerState;
  dispatch: Dispatch<WalkerAction>;
  onExit: () => void;
  onSaveClassification: SaveClassificationFn;
  saveErrorCount: number;
  pendingRetryCount: number;
  savedCount: number;
}) {
  const transitionPending = state.sectionTransitionPending;

  // R3+R10: text-entry mode. When the grader presses M or H, we open a
  // textarea instead of advancing immediately. Enter commits with text. Esc
  // or blur cancel cleanly — no row written, no advance, claim stays
  // unclassified — so an in-flight correction never gets silently dropped
  // when the grader tabs away mid-typing. C bypasses this entirely (no
  // correction text makes sense for a captured claim). State is local to
  // the Walker because it only exists during the brief in-claim text-entry
  // interaction.
  const [pendingTextEntry, setPendingTextEntry] = useState<{
    claimId: string;
    status: 'missed' | 'hallucinated';
    text: string;
  } | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-focus the textarea when it appears for a new claim/status.
  useEffect(() => {
    if (pendingTextEntry) {
      textareaRef.current?.focus();
    }
  }, [pendingTextEntry?.claimId, pendingTextEntry?.status]);

  function handleClassify(status: Exclude<ClaimStatus, null>) {
    if (state.cursor >= claims.length || transitionPending) return;
    const current = claims[state.cursor];

    if (status === 'captured') {
      // No correction text for captured. Fire save, advance.
      onSaveClassification(current, 'captured', null);
      dispatch({ type: 'classify', status: 'captured' });
      return;
    }
    if (status === 'skipped') {
      // Skip writes no row.
      dispatch({ type: 'classify', status: 'skipped' });
      return;
    }
    // missed / hallucinated → open textarea, don't advance yet.
    setPendingTextEntry({ claimId: current.id, status, text: '' });
  }

  function commitPendingTextEntry(text: string | null) {
    if (!pendingTextEntry) return;
    const claim = claims.find((c) => c.id === pendingTextEntry.claimId);
    if (!claim) {
      setPendingTextEntry(null);
      return;
    }
    onSaveClassification(claim, pendingTextEntry.status, text);
    dispatch({ type: 'classify', status: pendingTextEntry.status });
    setPendingTextEntry(null);
  }

  // Close the textarea without writing a row or advancing. Used by Esc and
  // blur so the claim stays unclassified and the grader can retry M/H or
  // pick a different status. Prevents silent data loss when focus leaves
  // mid-typing.
  function cancelPendingTextEntry() {
    setPendingTextEntry(null);
  }

  // Keyboard handling. Single global listener — torn down when the walker
  // unmounts (i.e. when the user returns to preview mode).
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      const target = e.target as HTMLElement | null;
      if (target) {
        const tag = target.tagName;
        if (tag === 'INPUT' || tag === 'TEXTAREA' || target.isContentEditable) {
          // The textarea handles its own Enter/Esc; the global handler
          // stays out of the way so the grader can type freely.
          return;
        }
      }
      if (e.metaKey || e.ctrlKey || e.altKey) return;

      // Block global shortcuts while text-entry is pending — the textarea
      // is the focused element by default, but a blur could otherwise leak
      // C/M/H presses into the walker mid-correction.
      if (pendingTextEntry) return;

      // When a section-transition interstitial is showing, only Enter
      // advances. Other keys are no-ops to avoid double-classifying past
      // the boundary.
      if (transitionPending) {
        if (e.key === 'Enter') {
          e.preventDefault();
          dispatch({ type: 'acknowledgeSectionTransition' });
        }
        return;
      }

      switch (e.key.toLowerCase()) {
        case 'c':
          e.preventDefault();
          handleClassify('captured');
          break;
        case 'm':
          e.preventDefault();
          handleClassify('missed');
          break;
        case 'h':
          e.preventDefault();
          handleClassify('hallucinated');
          break;
        case 's':
          e.preventDefault();
          handleClassify('skipped');
          break;
        case 'enter':
          e.preventDefault();
          dispatch({ type: 'advance' });
          break;
        case 'arrowleft':
        case 'j':
          e.preventDefault();
          dispatch({ type: 'back' });
          break;
        case 'arrowright':
        case 'k':
          e.preventDefault();
          dispatch({ type: 'forward' });
          break;
        case 'u':
          e.preventDefault();
          dispatch({ type: 'undo' });
          break;
      }
    }
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
    // handleClassify is stable enough at this granularity — we depend on
    // pendingTextEntry to gate it. Re-evaluated when transitionPending or
    // pendingTextEntry changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dispatch, transitionPending, pendingTextEntry, claims, state.cursor]);

  if (claims.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-background p-4 text-sm text-gray-300">
        <p>No gradable claims in this report. Sections may be empty or unavailable.</p>
        <button
          type="button"
          onClick={onExit}
          className="mt-3 rounded border border-border bg-surface px-3 py-1.5 text-sm text-white hover:bg-background"
        >
          Back to preview
        </button>
      </div>
    );
  }

  const isComplete = state.cursor >= claims.length;
  if (isComplete) {
    return (
      <SummaryScreen
        claims={claims}
        classifications={state.classifications}
        savedCount={savedCount}
        saveErrorCount={saveErrorCount}
        pendingRetryCount={pendingRetryCount}
        onExit={onExit}
      />
    );
  }

  if (transitionPending) {
    return (
      <SectionTransition
        claims={claims}
        cursor={state.cursor}
        classifications={state.classifications}
        onContinue={() => dispatch({ type: 'acknowledgeSectionTransition' })}
        onExit={onExit}
      />
    );
  }

  const current = claims[state.cursor];
  const sectionIndex = sectionOrderIndex(current.section_type);
  const sectionClaims = claims.filter((c) => c.section_type === current.section_type);
  const positionInSection = sectionClaims.findIndex((c) => c.id === current.id);
  const currentStatus = state.classifications[current.id] ?? null;

  return (
    <div className="flex h-full flex-col">
      {/* Walker header */}
      <div className="mb-3 flex items-center justify-between">
        <div className="text-xs uppercase tracking-wide text-brand">
          {sectionLabel(current.section_type)}
          <span className="ml-3 font-normal text-gray-400">
            Section {sectionIndex + 1} of {SECTION_ORDER.length} · Claim{' '}
            {positionInSection + 1} of {sectionClaims.length}
          </span>
        </div>
        <button
          type="button"
          onClick={onExit}
          className="rounded border border-border bg-background px-3 py-1 text-xs text-gray-300 hover:text-white"
        >
          Back to preview
        </button>
      </div>

      {/* Current claim */}
      <div className="my-4 flex-1 rounded-lg border border-border bg-background p-5">
        <p className="text-base leading-relaxed text-white">{current.text}</p>
      </div>

      {/* Button row 1 — classifications */}
      <div className="grid grid-cols-3 gap-2">
        <ClassifyButton
          label="Captured"
          keyHint="C"
          tone="captured"
          active={currentStatus === 'captured'}
          onClick={() => handleClassify('captured')}
          disabled={pendingTextEntry !== null}
        />
        <ClassifyButton
          label="Missed"
          keyHint="M"
          tone="missed"
          active={
            currentStatus === 'missed' ||
            (pendingTextEntry?.status === 'missed' && pendingTextEntry.claimId === current.id)
          }
          onClick={() => handleClassify('missed')}
          disabled={pendingTextEntry !== null}
        />
        <ClassifyButton
          label="Hallucinated"
          keyHint="H"
          tone="hallucinated"
          active={
            currentStatus === 'hallucinated' ||
            (pendingTextEntry?.status === 'hallucinated' &&
              pendingTextEntry.claimId === current.id)
          }
          onClick={() => handleClassify('hallucinated')}
          disabled={pendingTextEntry !== null}
        />
      </div>

      {/* Optional correction textarea — appears only when M or H is pending */}
      {pendingTextEntry && (
        <div className="mt-3 rounded border border-border bg-background p-3">
          <label className="block text-[10px] uppercase tracking-wide text-gray-500">
            Optional correction · Enter to save, Esc to cancel
          </label>
          <textarea
            ref={textareaRef}
            value={pendingTextEntry.text}
            onChange={(e) =>
              setPendingTextEntry((prev) =>
                prev ? { ...prev, text: e.target.value } : prev,
              )
            }
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const trimmed = pendingTextEntry.text.trim();
                commitPendingTextEntry(trimmed.length > 0 ? trimmed : null);
              } else if (e.key === 'Escape') {
                e.preventDefault();
                cancelPendingTextEntry();
              }
            }}
            onBlur={() => {
              // Blur = Esc per spec: close textarea, write no row, do not
              // advance, leave claim unclassified. Previously this called
              // commitPendingTextEntry(null), which wrote a row with NULL
              // correct_claim and advanced the walker — silently discarding
              // any in-flight text the grader had typed when they switched
              // windows or clicked outside. Cancel is the safe default; the
              // grader re-presses M/H to retry.
              cancelPendingTextEntry();
            }}
            placeholder='e.g. "TEX said 60%, actual is 75%". Enter to save, Esc to cancel.'
            rows={2}
            className="mt-1 w-full rounded border border-border bg-background px-2 py-1.5 text-sm text-white placeholder:text-gray-600 focus:border-brand focus:outline-none"
          />
        </div>
      )}

      {/* Button row 2 — utility */}
      <div className="mt-2 grid grid-cols-4 gap-2 text-xs">
        <UtilityButton
          label="Skip"
          keyHint="S"
          active={currentStatus === 'skipped'}
          onClick={() => handleClassify('skipped')}
          disabled={pendingTextEntry !== null}
        />
        <UtilityButton
          label="Back"
          keyHint="←"
          onClick={() => dispatch({ type: 'back' })}
          disabled={pendingTextEntry !== null}
        />
        <UtilityButton
          label="Forward"
          keyHint="→"
          onClick={() => dispatch({ type: 'forward' })}
          disabled={pendingTextEntry !== null}
        />
        <UtilityButton
          label="Undo"
          keyHint="U"
          onClick={() => dispatch({ type: 'undo' })}
          disabled={state.history.length === 0 || pendingTextEntry !== null}
        />
      </div>

      {/* Legend */}
      <p className="mt-3 text-[10px] text-gray-500">
        C captured · M missed · H hallucinated · S skip · ← back · → forward · U undo · Enter advance
      </p>

      {/* Persistence status — only visible when something interesting has happened. */}
      {(saveErrorCount > 0 || pendingRetryCount > 0) && (
        <p className="mt-2 rounded border border-red-500/40 bg-red-500/10 px-2 py-1 text-[11px] text-red-300">
          {saveErrorCount} save{saveErrorCount === 1 ? '' : 's'} failed
          {pendingRetryCount > 0 ? ` · ${pendingRetryCount} pending retry` : ''} — session
          continues, see summary on completion.
        </p>
      )}

      {/* Progress bar */}
      <div className="mt-3 h-0.5 w-full overflow-hidden rounded bg-border">
        <div
          className="h-full bg-brand transition-all"
          style={{ width: `${(state.cursor / claims.length) * 100}%` }}
        />
      </div>
    </div>
  );
}

function ClassifyButton({
  label,
  keyHint,
  tone,
  active,
  disabled,
  onClick,
}: {
  label: string;
  keyHint: string;
  tone: 'captured' | 'missed' | 'hallucinated';
  active: boolean;
  disabled?: boolean;
  onClick: () => void;
}) {
  const tones: Record<typeof tone, { base: string; active: string }> = {
    captured: {
      base: 'border-green-500/40 text-green-300 hover:bg-green-500/10',
      active: 'bg-green-500/20 text-green-200 border-green-500/70',
    },
    missed: {
      base: 'border-amber-500/40 text-amber-300 hover:bg-amber-500/10',
      active: 'bg-amber-500/20 text-amber-200 border-amber-500/70',
    },
    hallucinated: {
      base: 'border-red-500/40 text-red-300 hover:bg-red-500/10',
      active: 'bg-red-500/20 text-red-200 border-red-500/70',
    },
  };
  const cls = active ? tones[tone].active : tones[tone].base;
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`flex items-center justify-center gap-2 rounded border px-3 py-2 text-sm font-semibold transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${cls}`}
    >
      <span className="rounded bg-black/40 px-1.5 py-0.5 font-mono text-[10px]">
        {keyHint}
      </span>
      {label}
    </button>
  );
}

function UtilityButton({
  label,
  keyHint,
  active,
  disabled,
  onClick,
}: {
  label: string;
  keyHint: string;
  active?: boolean;
  disabled?: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`flex items-center justify-center gap-1.5 rounded border border-border bg-background px-2 py-1.5 text-gray-300 transition-colors hover:bg-surface hover:text-white disabled:cursor-not-allowed disabled:opacity-40 ${
        active ? 'bg-surface text-white' : ''
      }`}
    >
      <span className="rounded bg-black/40 px-1 py-0.5 font-mono text-[10px]">
        {keyHint}
      </span>
      {label}
    </button>
  );
}

function tallyFor(claims: Claim[], classifications: Classifications) {
  const counts = { captured: 0, missed: 0, hallucinated: 0, skipped: 0 };
  for (const c of claims) {
    const s = classifications[c.id];
    if (s === 'captured') counts.captured += 1;
    else if (s === 'missed') counts.missed += 1;
    else if (s === 'hallucinated') counts.hallucinated += 1;
    else if (s === 'skipped') counts.skipped += 1;
  }
  return counts;
}

function SectionTransition({
  claims,
  cursor,
  classifications,
  onContinue,
  onExit,
}: {
  claims: Claim[];
  cursor: number;
  classifications: Classifications;
  onContinue: () => void;
  onExit: () => void;
}) {
  // Cursor points at the first claim of the *next* section. The section
  // just completed is the one before it.
  const completedSection = claims[cursor - 1].section_type;
  const nextSection = claims[cursor].section_type;
  const completedClaims = claims.filter((c) => c.section_type === completedSection);
  const counts = tallyFor(completedClaims, classifications);

  return (
    <div className="rounded-lg border border-border bg-background p-6 text-sm text-gray-200">
      <p className="text-base font-semibold text-white">
        ✓ {sectionLabel(completedSection)} complete
      </p>
      <p className="mt-3 text-gray-300">
        {completedClaims.length} claims · {counts.captured} captured · {counts.missed} missed ·{' '}
        {counts.hallucinated} hallucinated · {counts.skipped} skipped
      </p>
      <p className="mt-4 text-white">Continue to {sectionLabel(nextSection)}?</p>
      <div className="mt-4 flex gap-2">
        <button
          type="button"
          onClick={onContinue}
          className="rounded bg-brand px-4 py-2 text-sm font-semibold text-black hover:bg-orange-400"
        >
          Enter or Continue
        </button>
        <button
          type="button"
          onClick={onExit}
          className="rounded border border-border bg-surface px-4 py-2 text-sm text-gray-300 hover:text-white"
        >
          Stop and go back to preview
        </button>
      </div>
    </div>
  );
}

function SummaryScreen({
  claims,
  classifications,
  savedCount,
  saveErrorCount,
  pendingRetryCount,
  onExit,
}: {
  claims: Claim[];
  classifications: Classifications;
  savedCount: number;
  saveErrorCount: number;
  pendingRetryCount: number;
  onExit: () => void;
}) {
  const overall = tallyFor(claims, classifications);
  const total = claims.length;
  const pct = (n: number) => (total === 0 ? '0' : Math.round((n / total) * 100).toString());

  const perSection = SECTION_ORDER.map((s) => {
    const sectionClaims = claims.filter((c) => c.section_type === s);
    if (sectionClaims.length === 0) return null;
    const counts = tallyFor(sectionClaims, classifications);
    return { section_type: s, total: sectionClaims.length, counts };
  }).filter((s): s is NonNullable<typeof s> => s !== null);

  return (
    <div className="rounded-lg border border-border bg-background p-6 text-sm text-gray-200">
      <h3 className="text-base font-semibold text-white">Grading session complete</h3>

      <div className="mt-4 space-y-1">
        <p className="text-gray-300">
          Total: <span className="text-white">{total}</span> claims
        </p>
        <p className="text-green-300">
          Captured: <span className="font-semibold">{overall.captured}</span> ({pct(overall.captured)}%)
        </p>
        <p className="text-amber-300">
          Missed: <span className="font-semibold">{overall.missed}</span> ({pct(overall.missed)}%)
        </p>
        <p className="text-red-300">
          Hallucinated: <span className="font-semibold">{overall.hallucinated}</span> (
          {pct(overall.hallucinated)}%)
        </p>
        <p className="text-gray-400">
          Skipped: <span className="font-semibold">{overall.skipped}</span> ({pct(overall.skipped)}%)
        </p>
      </div>

      <div className="mt-5">
        <p className="mb-2 text-xs uppercase tracking-wide text-gray-500">Per section</p>
        <ul className="space-y-1 text-xs text-gray-300">
          {perSection.map((s) => (
            <li key={s.section_type}>
              {sectionLabel(s.section_type)} — {s.total} ({s.counts.captured} / {s.counts.missed} /{' '}
              {s.counts.hallucinated} / {s.counts.skipped})
            </li>
          ))}
        </ul>
      </div>

      {/* R3+R10: save status. The memory-only warning is gone — classifications
          persist as they happen. A red banner shows only if the network had
          trouble; otherwise the green confirmation tells the grader the
          session is durable. */}
      <div className="mt-5 rounded border border-border bg-surface px-3 py-2 text-xs">
        <p className="text-green-300">
          {savedCount} correction{savedCount === 1 ? '' : 's'} written to DB.
        </p>
        {(saveErrorCount > 0 || pendingRetryCount > 0) && (
          <p className="mt-1 text-red-300">
            ⚠ {saveErrorCount} failed
            {pendingRetryCount > 0 ? ` · ${pendingRetryCount} retained for retry` : ''}.
            Check the browser console / network tab.
          </p>
        )}
      </div>

      <p className="mt-3 rounded border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-xs text-amber-200">
        EVAL_SCORES.md entry and disk snapshot will be written by R11 + R12. This session&apos;s
        scores are not yet recorded permanently.
      </p>

      <button
        type="button"
        onClick={onExit}
        className="mt-4 rounded border border-border bg-surface px-4 py-2 text-sm text-white hover:bg-background"
      >
        Back to preview
      </button>
    </div>
  );
}
