'use client';

import { Dispatch, useCallback, useEffect, useReducer } from 'react';
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
}: {
  claims: Claim[];
  state: WalkerState;
  dispatch: Dispatch<WalkerAction>;
  onExit: () => void;
}) {
  const transitionPending = state.sectionTransitionPending;

  // Keyboard handling. Single global listener — torn down when the walker
  // unmounts (i.e. when the user returns to preview mode).
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      const target = e.target as HTMLElement | null;
      if (target) {
        const tag = target.tagName;
        if (tag === 'INPUT' || tag === 'TEXTAREA' || target.isContentEditable) {
          return;
        }
      }
      if (e.metaKey || e.ctrlKey || e.altKey) return;

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
          dispatch({ type: 'classify', status: 'captured' });
          break;
        case 'm':
          e.preventDefault();
          dispatch({ type: 'classify', status: 'missed' });
          break;
        case 'h':
          e.preventDefault();
          dispatch({ type: 'classify', status: 'hallucinated' });
          break;
        case 's':
          e.preventDefault();
          dispatch({ type: 'classify', status: 'skipped' });
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
  }, [dispatch, transitionPending]);

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
    return <SummaryScreen claims={claims} classifications={state.classifications} onExit={onExit} />;
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
          onClick={() => dispatch({ type: 'classify', status: 'captured' })}
        />
        <ClassifyButton
          label="Missed"
          keyHint="M"
          tone="missed"
          active={currentStatus === 'missed'}
          onClick={() => dispatch({ type: 'classify', status: 'missed' })}
        />
        <ClassifyButton
          label="Hallucinated"
          keyHint="H"
          tone="hallucinated"
          active={currentStatus === 'hallucinated'}
          onClick={() => dispatch({ type: 'classify', status: 'hallucinated' })}
        />
      </div>

      {/* Button row 2 — utility */}
      <div className="mt-2 grid grid-cols-4 gap-2 text-xs">
        <UtilityButton
          label="Skip"
          keyHint="S"
          active={currentStatus === 'skipped'}
          onClick={() => dispatch({ type: 'classify', status: 'skipped' })}
        />
        <UtilityButton
          label="Back"
          keyHint="←"
          onClick={() => dispatch({ type: 'back' })}
        />
        <UtilityButton
          label="Forward"
          keyHint="→"
          onClick={() => dispatch({ type: 'forward' })}
        />
        <UtilityButton
          label="Undo"
          keyHint="U"
          onClick={() => dispatch({ type: 'undo' })}
          disabled={state.history.length === 0}
        />
      </div>

      {/* Legend */}
      <p className="mt-3 text-[10px] text-gray-500">
        C captured · M missed · H hallucinated · S skip · ← back · → forward · U undo · Enter advance
      </p>

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
  onClick,
}: {
  label: string;
  keyHint: string;
  tone: 'captured' | 'missed' | 'hallucinated';
  active: boolean;
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
      className={`flex items-center justify-center gap-2 rounded border px-3 py-2 text-sm font-semibold transition-colors ${cls}`}
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
  onExit,
}: {
  claims: Claim[];
  classifications: Classifications;
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

      <p className="mt-5 rounded border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-xs text-amber-200">
        ⚠ Classifications held in memory only. Save wiring lands in R3+R10.
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
