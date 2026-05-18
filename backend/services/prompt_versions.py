"""Prompt version strings used for `film_analysis_cache` lookup.

The table stores both Prompts 0A/0B output (`synthesis_document`) and, after a
report completes, sections 1-4 (`sections` jsonb). A single `prompt_version`
column must change when *either* the pre-process prompts or the six section
prompts change, so we do not read stale synthesis or stale sections.

Format: `{sections_prompt_version}|{preprocess_prompt_version}`
  - sections: `VERSION:` line in `offensive_sets.txt` (same bundle as the other
    five section prompts — keep them aligned via PROMPTS.md / release practice)
  - preprocess: `chunk_extraction` and `chunk_synthesis` headers; if those two
    differ, they are joined with `+` before the `|` above.
"""

from __future__ import annotations

import logging

from services.prompts import load_prompt

log = logging.getLogger(__name__)


def get_film_analysis_cache_prompt_version() -> str:
    """Value for `film_analysis_cache.prompt_version` and lookup queries."""
    _, sections_v = load_prompt("offensive_sets")
    _, v0a = load_prompt("chunk_extraction")
    _, v0b = load_prompt("chunk_synthesis")
    if v0a != v0b:
        log.warning(
            "chunk_extraction VERSION (%s) != chunk_synthesis VERSION (%s); "
            "preprocess key will be %s+%s",
            v0a,
            v0b,
            v0a,
            v0b,
        )
        preprocess_v = f"{v0a}+{v0b}"
    else:
        preprocess_v = v0a
    return f"{sections_v}|{preprocess_v}"
