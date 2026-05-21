'use client';

import { useAuth } from '@clerk/nextjs';
import { useParams } from 'next/navigation';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  AdminReportDetail,
  AdminReportSection,
  GoldenFilm,
  GradingCorrectionInput,
  GradingSessionRollup,
  GroundTruthDocument,
  completeGradingSession,
  createGradingCorrection,
  getAdminReportDetail,
  getGoldenTruth,
  listGoldenFilms,
} from '@/lib/api';
import { SECTION_LABELS, sectionOrderIndex } from '@/lib/grading/sections';
import { Claim } from '@/lib/grading/splitClaims';
import Walker, { buildSortedClaims, useWalkerReducer } from './Walker';

type Mode = 'preview' | 'walker';

function sortSections(sections: AdminReportSection[]): AdminReportSection[] {
  return [...sections].sort(
    (a, b) => sectionOrderIndex(a.section_type) - sectionOrderIndex(b.section_type),
  );
}

export default function GradeReportPage() {
  const { report_id: reportId } = useParams<{ report_id: string }>();
  const { getToken } = useAuth();

  // Report (right pane)
  const [report, setReport] = useState<AdminReportDetail | null>(null);
  const [reportLoading, setReportLoading] = useState(true);
  const [reportError, setReportError] = useState<string | null>(null);

  // Golden film list (header dropdown)
  const [films, setFilms] = useState<GoldenFilm[]>([]);
  const [filmsError, setFilmsError] = useState<string | null>(null);

  // Ground truth (left pane)
  const [selectedSlug, setSelectedSlug] = useState<string>('');
  const [groundTruth, setGroundTruth] = useState<GroundTruthDocument | null>(null);
  const [gtLoading, setGtLoading] = useState(false);
  const [gtError, setGtError] = useState<string | null>(null);

  // Right-pane mode toggle. Walker state lives at this level so it
  // survives mode toggles (preview ↔ walker) within the same page-load.
  const [mode, setMode] = useState<Mode>('preview');

  // Load report once on mount.
  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const token = await getToken();
        if (!token) {
          if (!cancelled) setReportError('Not authenticated');
          return;
        }
        const data = await getAdminReportDetail(token, reportId);
        if (!cancelled) setReport(data);
      } catch (e) {
        if (!cancelled) {
          setReportError(e instanceof Error ? e.message : 'Failed to load report');
        }
      } finally {
        if (!cancelled) setReportLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [reportId, getToken]);

  // Load golden-film list once on mount.
  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const token = await getToken();
        if (!token) return;
        const data = await listGoldenFilms(token);
        if (!cancelled) setFilms(data);
      } catch (e) {
        if (!cancelled) {
          setFilmsError(e instanceof Error ? e.message : 'Failed to load golden films');
        }
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [getToken]);

  // Load ground truth whenever the selected film changes.
  useEffect(() => {
    if (!selectedSlug) {
      setGroundTruth(null);
      setGtError(null);
      setGtLoading(false);
      return;
    }
    let cancelled = false;
    async function load() {
      setGtLoading(true);
      setGtError(null);
      setGroundTruth(null);
      try {
        const token = await getToken();
        if (!token) {
          if (!cancelled) setGtError('Not authenticated');
          return;
        }
        const data = await getGoldenTruth(token, selectedSlug);
        if (!cancelled) setGroundTruth(data);
      } catch (e) {
        if (!cancelled) {
          setGtError(e instanceof Error ? e.message : 'Failed to load ground truth');
        }
      } finally {
        if (!cancelled) setGtLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [selectedSlug, getToken]);

  const sortedSections = useMemo(
    () => (report ? sortSections(report.sections) : []),
    [report],
  );

  // Build claims once per report. Walker reads from this list; preview
  // mode doesn't need it. State (cursor / classifications / history)
  // lives in useWalkerReducer and persists across mode toggles.
  const claims = useMemo(() => buildSortedClaims(sortedSections), [sortedSections]);
  const [walkerState, walkerDispatch] = useWalkerReducer(claims);

  // R3+R10: persistence counters. savedCount increments on a successful POST;
  // saveErrorCount on any failure; pendingRetries accumulates failed payloads
  // for the summary screen so a flaky network doesn't quietly lose work.
  // A pendingRetries-driven background retry loop is out of scope; the
  // grader sees the count and can re-run the session if needed.
  const [savedCount, setSavedCount] = useState(0);
  const [saveErrorCount, setSaveErrorCount] = useState(0);
  const [pendingRetries, setPendingRetries] = useState<GradingCorrectionInput[]>([]);

  // Per-section prompt_version lookup. The walker writes the section's own
  // version, not the report's top-level version, because sections can run
  // different prompt versions in the same report.
  const promptVersionBySection = useMemo(() => {
    const map: Record<string, string> = {};
    for (const s of sortedSections) {
      map[s.section_type] = s.prompt_version;
    }
    return map;
  }, [sortedSections]);

  // Single film_id for the report — current data model assumes one film
  // per report (report_films may carry more, but the walker context wants
  // a single anchor for now). If multi-film reports become real, this
  // becomes the first film and a TODO surfaces.
  const filmId = report?.films[0]?.film_id ?? null;

  // Hold the token in a ref so onSaveClassification can be a stable callback
  // without forcing the parent to re-render every keystroke. We refresh the
  // token lazily inside the save path.
  const getTokenRef = useRef(getToken);
  useEffect(() => {
    getTokenRef.current = getToken;
  }, [getToken]);

  const onSaveClassification = useCallback(
    (claim: Claim, status: 'captured' | 'missed' | 'hallucinated', correctText: string | null) => {
      if (!report || !filmId) {
        // Without report/film context there's nothing to anchor a row to.
        // Increment failure count so the summary surface reflects the gap.
        setSaveErrorCount((n) => n + 1);
        return;
      }
      const promptVersion =
        promptVersionBySection[claim.section_type] ?? report.report_prompt_version;
      const payload: GradingCorrectionInput = {
        report_id: report.report_id,
        film_id: filmId,
        section_type: claim.section_type,
        claim_status: status,
        ai_claim: claim.text,
        correct_claim: correctText,
        // Walker rows are intentionally bucketed as 'walker_v1' — see
        // backend VALID_CATEGORIES comment. Pattern analyzer slices walker
        // data by claim_status × section_type × prompt_version, not category.
        category: 'walker_v1',
        prompt_version: promptVersion,
      };

      // Fire-and-forget. We snapshot the token outside the await so the
      // walker can keep moving while this resolves.
      (async () => {
        try {
          const token = await getTokenRef.current();
          if (!token) {
            setSaveErrorCount((n) => n + 1);
            setPendingRetries((prev) => [...prev, payload]);
            return;
          }
          await createGradingCorrection(token, payload);
          setSavedCount((n) => n + 1);
        } catch (err) {
          // Per spec: never block the walker. Surface count, retain for
          // retry, log to console so DevTools network-tab debugging works.
          // eslint-disable-next-line no-console
          console.error('createGradingCorrection failed', err, payload);
          setSaveErrorCount((n) => n + 1);
          setPendingRetries((prev) => [...prev, payload]);
        }
      })();
    },
    [report, filmId, promptVersionBySection],
  );

  // R11: lock the session start time the first time the grader enters
  // walker mode. The summary screen passes this as the lower bound when
  // rolling up walker_v1 corrections rows so re-grades against the same
  // report each get their own EVAL_SCORES row. Captured in a ref so it
  // never moves once set; reset on full page reload (acceptable for v1).
  const sessionStartedAtRef = useRef<string | null>(null);
  useEffect(() => {
    if (mode === 'walker' && sessionStartedAtRef.current === null) {
      sessionStartedAtRef.current = new Date().toISOString();
    }
  }, [mode]);

  const onCompleteSession = useCallback(async (): Promise<GradingSessionRollup> => {
    if (!report) throw new Error('Report not loaded');
    const sessionStartedAt = sessionStartedAtRef.current;
    if (!sessionStartedAt) throw new Error('Session start time not set');
    const token = await getTokenRef.current();
    if (!token) throw new Error('Not authenticated');
    return completeGradingSession(token, {
      report_id: report.report_id,
      prompt_version: report.report_prompt_version,
      session_started_at: sessionStartedAt,
    });
  }, [report]);

  const canStartGrading = !!report && !!filmId && claims.length > 0;

  return (
    <div className="-mx-6 -mt-6">
      {/* Header strip */}
      <div className="sticky top-0 z-10 flex items-center justify-between border-b border-border bg-background px-6 py-3">
        <div className="text-sm text-white">
          <span className="text-gray-400">Grading:</span>{' '}
          <span className="font-semibold">
            {report ? report.team_name : reportLoading ? '...' : 'unknown team'}
          </span>
          <span className="mx-2 text-gray-500">·</span>
          <span className="text-gray-400">prompt</span>{' '}
          <span className="font-mono text-xs text-white">
            {report ? report.report_prompt_version : '—'}
          </span>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <label className="text-gray-400" htmlFor="golden-film-select">
            film:
          </label>
          <select
            id="golden-film-select"
            value={selectedSlug}
            onChange={(e) => setSelectedSlug(e.target.value)}
            className="rounded border border-border bg-background px-2 py-1 text-sm text-white"
          >
            <option value="">— select golden film —</option>
            {films.map((f) => (
              <option key={f.slug} value={f.slug}>
                {f.display_name}
              </option>
            ))}
          </select>
          {filmsError && <span className="text-xs text-red-400">{filmsError}</span>}
        </div>
      </div>

      {/* Two-pane body. Each pane scrolls independently. */}
      <div className="grid grid-cols-2 gap-4 px-6 py-4">
        {/* Left pane — Ground Truth */}
        <div className="h-[calc(100vh-180px)] overflow-y-auto rounded-lg border border-border bg-surface p-4">
          <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-brand">
            Ground Truth
          </h2>
          {!selectedSlug && !gtLoading && (
            <p className="text-sm text-gray-400">
              Select a golden film to load ground truth.
            </p>
          )}
          {gtLoading && <p className="text-sm text-gray-400">Loading ground truth...</p>}
          {gtError && (
            <p className="rounded bg-red-900/50 px-3 py-2 text-sm text-red-300">{gtError}</p>
          )}
          {groundTruth && (
            <div className="grading-markdown text-sm leading-relaxed text-gray-200">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {groundTruth.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Right pane — TEX Report (preview) or Walker */}
        <div className="h-[calc(100vh-180px)] overflow-y-auto rounded-lg border border-border bg-surface p-4">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-xs font-semibold uppercase tracking-wide text-brand">
              {mode === 'walker' ? 'Walker' : 'TEX Report'}
            </h2>
            {mode === 'preview' && canStartGrading && (
              <button
                type="button"
                onClick={() => setMode('walker')}
                className="rounded bg-brand px-3 py-1 text-xs font-semibold text-black hover:bg-orange-400"
              >
                Start grading
              </button>
            )}
          </div>

          {mode === 'preview' ? (
            <>
              {reportLoading && <p className="text-sm text-gray-400">Loading report...</p>}
              {reportError && (
                <p className="rounded bg-red-900/50 px-3 py-2 text-sm text-red-300">
                  {reportError}
                </p>
              )}
              {report && (
                <>
                  <div className="mb-4 space-y-1 text-xs text-gray-400">
                    <div>
                      <span className="text-gray-500">status:</span>{' '}
                      <span className="text-white">{report.status}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">completed:</span>{' '}
                      <span className="text-white">
                        {report.completed_at
                          ? new Date(report.completed_at).toLocaleString()
                          : 'not complete'}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500">report id:</span>{' '}
                      <span className="font-mono text-white">{report.report_id}</span>
                    </div>
                    {report.films.length > 0 && (
                      <div>
                        <span className="text-gray-500">films:</span>{' '}
                        <span className="text-white">
                          {report.films.map((f) => f.file_name).join(', ')}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="space-y-4">
                    {sortedSections.map((s) => (
                      <SectionBlock key={s.section_type} section={s} />
                    ))}
                    {sortedSections.length === 0 && (
                      <p className="text-sm text-gray-400">No sections found.</p>
                    )}
                  </div>
                </>
              )}
            </>
          ) : (
            <Walker
              claims={claims}
              state={walkerState}
              dispatch={walkerDispatch}
              onExit={() => setMode('preview')}
              onSaveClassification={onSaveClassification}
              onCompleteSession={onCompleteSession}
              savedCount={savedCount}
              saveErrorCount={saveErrorCount}
              pendingRetryCount={pendingRetries.length}
            />
          )}
        </div>
      </div>

      {/* Minimal scoped markdown styling. Avoids adding the typography
          plugin (not installed) while still rendering headers and tables
          legibly inside the dark grading canvas. */}
      <style jsx global>{`
        .grading-markdown h1 {
          font-size: 1.125rem;
          font-weight: 700;
          color: #fff;
          margin: 1rem 0 0.5rem;
        }
        .grading-markdown h2 {
          font-size: 1rem;
          font-weight: 700;
          color: #fff;
          margin: 0.9rem 0 0.4rem;
        }
        .grading-markdown h3 {
          font-size: 0.9rem;
          font-weight: 600;
          color: #fff;
          margin: 0.8rem 0 0.3rem;
        }
        .grading-markdown p {
          margin: 0.5rem 0;
        }
        .grading-markdown ul,
        .grading-markdown ol {
          margin: 0.5rem 0 0.5rem 1.25rem;
          list-style: disc;
        }
        .grading-markdown ol {
          list-style: decimal;
        }
        .grading-markdown li {
          margin: 0.15rem 0;
        }
        .grading-markdown strong {
          color: #fff;
        }
        .grading-markdown code {
          background: #0a0a0a;
          padding: 0 0.25rem;
          border-radius: 3px;
          font-size: 0.85em;
        }
        .grading-markdown pre {
          background: #0a0a0a;
          padding: 0.6rem;
          border-radius: 4px;
          overflow-x: auto;
          font-size: 0.8rem;
        }
        .grading-markdown blockquote {
          border-left: 2px solid #f97316;
          padding-left: 0.75rem;
          margin: 0.6rem 0;
          color: #d4d4d4;
        }
        .grading-markdown table {
          border-collapse: collapse;
          margin: 0.6rem 0;
          font-size: 0.8rem;
          width: 100%;
        }
        .grading-markdown th,
        .grading-markdown td {
          border: 1px solid #262626;
          padding: 0.3rem 0.5rem;
          vertical-align: top;
        }
        .grading-markdown th {
          background: #1a1a1a;
          font-weight: 600;
          text-align: left;
        }
        .grading-markdown hr {
          border: 0;
          border-top: 1px solid #262626;
          margin: 0.8rem 0;
        }
        .grading-markdown a {
          color: #f97316;
          text-decoration: underline;
        }
      `}</style>
    </div>
  );
}

function SectionBlock({ section }: { section: AdminReportSection }) {
  const label = SECTION_LABELS[section.section_type] ?? section.section_type;
  const isAvailable = section.status === 'complete' && section.content;

  return (
    <div className="rounded-lg border border-border bg-background p-3">
      <div className="mb-2 flex items-baseline justify-between gap-2">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-brand">{label}</h3>
        <div className="text-[10px] text-gray-500">
          <span className="font-mono">{section.prompt_version}</span>
          {section.model_used && (
            <>
              <span className="mx-1">·</span>
              <span>{section.model_used}</span>
            </>
          )}
          <span className="mx-1">·</span>
          <span>{section.status}</span>
        </div>
      </div>
      {isAvailable ? (
        <div className="whitespace-pre-wrap text-sm leading-relaxed text-gray-200">
          {section.content}
        </div>
      ) : (
        <p className="text-sm italic text-gray-500">
          Section not available
          {section.error_message ? ` — ${section.error_message}` : ''}.
        </p>
      )}
    </div>
  );
}
