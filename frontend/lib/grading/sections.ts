// Canonical PDF order. Mirrors backend CANONICAL_SECTION_ORDER in
// admin.py — keep client-side too so any missing rows fall to the end
// in a predictable place instead of crashing the page.
export const SECTION_ORDER = [
  'offensive_sets',
  'defensive_schemes',
  'pnr_coverage',
  'player_pages',
  'game_plan',
  'adjustments_practice',
] as const;

export type SectionType = (typeof SECTION_ORDER)[number];

export const SECTION_LABELS: Record<string, string> = {
  offensive_sets: 'Offensive Sets',
  defensive_schemes: 'Defensive Schemes',
  pnr_coverage: 'Pick & Roll Coverage',
  player_pages: 'Player Pages',
  game_plan: 'Game Plan',
  adjustments_practice: 'Adjustments & Practice',
};

export function sectionLabel(section_type: string): string {
  return SECTION_LABELS[section_type] ?? section_type;
}

export function sectionOrderIndex(section_type: string): number {
  const i = (SECTION_ORDER as readonly string[]).indexOf(section_type);
  return i === -1 ? SECTION_ORDER.length : i;
}
