// V1 sentence-split for the grading walker (R9).
//
// Deliberately simple. Compound sentences become a single claim — Tommy
// uses Skip (S) for non-claims and the correction text field (R3+R10)
// to note compound-claim nuance. Structured-claim upgrade is post-MVP.
//
// Rules (in order):
//   1. Strip markdown noise: pure-header lines (`### **OFFENSIVE SETS**`),
//      pure bold-line decorations (`**1. PRIMARY HALF-COURT OFFENSE**`),
//      horizontal rules, and blank lines are dropped before splitting.
//   2. Split remaining text on sentence-terminating punctuation: `.`, `!`,
//      `?` followed by whitespace or end-of-string.
//   3. Trim each resulting sentence. Drop any shorter than 15 characters
//      (filters out artifacts like "**1.**" or stray bullets).
//   4. Preserve order. Assign `index` as the 0-based position within the
//      section's claim list.
//
// Worked examples (smoke):
//
//   input:  "### **OFFENSIVE SETS**\n\nThey run Horns from the right side ~60% of the time. They prefer the high pick-and-roll."
//   output: [
//     { text: "They run Horns from the right side ~60% of the time.", index: 0 },
//     { text: "They prefer the high pick-and-roll.", index: 1 },
//   ]
//
//   input:  "**1. PRIMARY HALF-COURT OFFENSE**\n\nThe ball-handler is #3 Smith."
//   output: [
//     { text: "The ball-handler is #3 Smith.", index: 0 },
//   ]
//
//   input:  "Short."
//   output: []   // under 15 chars
//
//   input:  ""
//   output: []
//
//   input:  "Defense plays man-to-man. They switch on screens! What about traps? Yes, sometimes."
//   output: [
//     { text: "Defense plays man-to-man.", index: 0 },
//     { text: "They switch on screens!", index: 1 },
//     { text: "What about traps?", index: 2 },
//     { text: "Yes, sometimes.", index: 3 },
//   ]

export type Claim = {
  id: string;
  section_type: string;
  text: string;
  index: number;
};

const MIN_CLAIM_LENGTH = 15;

// Lines we drop wholesale before splitting:
//   - markdown headers (#, ##, ###, ####, ...)
//   - horizontal rules
//   - lines that are nothing but bold-wrapped text (decoration headers)
//   - blank lines (after trim)
const PURE_HEADER_RE = /^#{1,6}\s+.*$/;
const PURE_BOLD_DECORATION_RE = /^\s*\*\*[^*]+\*\*\s*$/;
const HORIZONTAL_RULE_RE = /^-{3,}\s*$|^={3,}\s*$|^\*{3,}\s*$/;

function stripMarkdownNoise(content: string): string {
  return content
    .split(/\r?\n/)
    .filter((line) => {
      const trimmed = line.trim();
      if (trimmed.length === 0) return false;
      if (PURE_HEADER_RE.test(trimmed)) return false;
      if (PURE_BOLD_DECORATION_RE.test(trimmed)) return false;
      if (HORIZONTAL_RULE_RE.test(trimmed)) return false;
      return true;
    })
    .join(' ');
}

// Split on `.`, `!`, `?` followed by whitespace. Lookbehind keeps the
// terminator attached to the preceding sentence. Trailing fragment (last
// sentence, no trailing whitespace) falls out as the final array element.
const SENTENCE_SPLIT_RE = /(?<=[.!?])\s+/;

export function splitClaims(section_type: string, content: string | null): Claim[] {
  if (!content) return [];
  const flattened = stripMarkdownNoise(content);
  if (flattened.length === 0) return [];

  const candidates = flattened.split(SENTENCE_SPLIT_RE);

  const claims: Claim[] = [];
  let index = 0;
  for (const raw of candidates) {
    const text = raw.trim();
    if (text.length < MIN_CLAIM_LENGTH) continue;
    claims.push({
      id: `${section_type}-${index}`,
      section_type,
      text,
      index,
    });
    index += 1;
  }
  return claims;
}
