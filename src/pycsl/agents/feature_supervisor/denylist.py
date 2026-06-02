from __future__ import annotations
import argparse, datetime, json, os, re, subprocess, sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from ._common import *

__all__ = [
    'load_deny_list',
    'is_load_bearing',
]

def load_deny_list() -> List[str]:
    """Parse the deny-list from the load-bearing-files.md fenced block."""
    if not _LOAD_BEARING_FILE.is_file():
        return []
    text = _LOAD_BEARING_FILE.read_text()
    # First triple-backtick fence block contains the deny-list paths
    m = re.search(r"```\n(.*?)\n```", text, re.S)
    if not m:
        return []
    return [
        line.strip()
        for line in m.group(1).splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def is_load_bearing(target: str, deny_list: List[str]) -> Optional[str]:
    """Return the matched deny-list entry if `target` is load-bearing."""
    # Normalise: a feature plan may quote paths with backticks, leading
    # slashes, or repo-relative form. Strip noise.
    cleaned = target.strip().strip("`").lstrip("./").lstrip("/")
    for entry in deny_list:
        e = entry.strip()
        if not e:
            continue
        # Directory entry (ends with /): match if target is under it
        if e.endswith("/"):
            if cleaned.startswith(e) or cleaned == e.rstrip("/"):
                return e
        # File entry: match if target ends with it
        elif cleaned.endswith(e) or cleaned == e:
            return e
    return None


# ---------------------------------------------------------------------------
# Feature-plan parser
# ---------------------------------------------------------------------------

# ---- Extreme Rigor: acceptance claims ----------------------------------
#
# Per feature-supervisor-extreme-rigor.md: every non-DONE phase carries an
# `**Acceptance:**` block whose bullets the supervisor executes. Each bullet
# is `\`command\` <predicate>` where predicate is one of:
#   `exits N`                        — exit code == N (default 0)
#   `stdout == \`value\``            — stdout (stripped) == value
#   `stdout >= \`N\``                — stdout (parsed as int) >= N
#   `stdout matches \`regex\``       — re.search(regex, stdout) hits
#
# A phase may carry `**Acceptance:** none — <reason>` to opt out
# explicitly (research/docs-only phases).

