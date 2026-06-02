from __future__ import annotations
import argparse, datetime, json, os, re, subprocess, sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from llm_client import log  # noqa: E402

__all__ = [
    'log',
    '_SCRIPT_DIR',
    '_PROJECT_ROOT',
    'AGENT_NAME',
    'EXIT_OK',
    'EXIT_GATE_FAIL',
    'EXIT_HUMAN_NEEDED',
    'EXIT_ROLLBACK_FAIL',
    'REASON_MISSING_ACCEPTANCE',
    'REASON_STATUS_FORGED',
    'REASON_ACCEPTANCE_FAILED',
    'REASON_CLAIM_REJECTED',
    '_LOAD_BEARING_FILE',
    '_HALT_REPORT_ROOT',
    '_BRIDGE_CURSOR',
    '_METRICS_LOGS',
    '_CODING_LLM_PROMPT',
    '_AGENT_DESCRIPTION',
    '_SKILLS_ROOT',
    '_COMPETENCY_FILE',
    '_DEFAULT_TIMEOUT_SEC',
    '_DEEP_MODE',
    '_git',
    '_phase_tag',
    '_slug',
]

# This module lives at <repo>/src/pycsl/agents/feature_supervisor/_common.py,
# so the repo root is parents[4]. (_SCRIPT_DIR keeps pointing at the agents/
# dir — the package's parent — for any agents-relative use.)
_SCRIPT_DIR = Path(__file__).resolve().parents[1]      # <repo>/src/pycsl/agents
_PROJECT_ROOT = Path(__file__).resolve().parents[4]    # <repo>

# Mirror agent-stdlib-annotate.py's pattern: re-use the shared LLM
# client log() helper (we do not use llm_generate in v1 — supervisor
# is gate-only, no LLM calls).
sys.path.insert(0, str(_PROJECT_ROOT / "src" / "pycsl" / "agents"))
from llm_client import log  # noqa: E402

AGENT_NAME = "agent-feature-supervisor"

# Exit-code convention extends coordinator.py:
EXIT_OK = 0
EXIT_GATE_FAIL = 74
EXIT_HUMAN_NEEDED = 75
EXIT_ROLLBACK_FAIL = 76

# ER halt reason codes (all map to exit 75 — human-needed).
# Reported in halt-report header and run-log so the failure mode is
# unambiguous.
REASON_MISSING_ACCEPTANCE = "MISSING_ACCEPTANCE"
REASON_STATUS_FORGED = "STATUS_FORGED"
REASON_ACCEPTANCE_FAILED = "ACCEPTANCE_FAILED"
REASON_CLAIM_REJECTED = "CLAIM_REJECTED"

_LOAD_BEARING_FILE = (
    _PROJECT_ROOT
    / "config"
    / "skills"
    / "agent-stdlib-annotate"
    / "references"
    / "load-bearing-files.md"
)

_HALT_REPORT_ROOT = _PROJECT_ROOT / "metrics" / "feature-supervisor"
_BRIDGE_CURSOR = _PROJECT_ROOT / "projects" / "pycsl" / "message-queues" / ".bridge-cursor.json"
_METRICS_LOGS = _PROJECT_ROOT / "metrics" / "logs"

_CODING_LLM_PROMPT = (
    _PROJECT_ROOT
    / "config"
    / "skills"
    / "agent-stdlib-annotate"
    / "references"
    / "coding-llm-prompt.md"
)

# The supervisor's own persona / ER discipline. Loaded into LLM
# delegation prompts so a delegate operates under the same Extreme
# Rigor rules this module enforces. (Gap 11 of the post-implementation
# retrospective: the persona doc existed but nothing read it.)
_AGENT_DESCRIPTION = (
    _PROJECT_ROOT
    / "config"
    / "agents"
    / "agent-feature-supervisor.md"
)

# Competency matrix (skill-to-role) — which skills each level needs, read by
# the resolver to inject role-appropriate skills into delegate prompts and to
# log the resolution in the harness-structure record's `## 5` section.
_SKILLS_ROOT = _PROJECT_ROOT / "config" / "skills"
_COMPETENCY_FILE = (
    _SKILLS_ROOT / "project-lifecycle" / "references" / "competency-matrix.md"
)


# ---------------------------------------------------------------------------
# Load-bearing deny-list
# ---------------------------------------------------------------------------

_DEFAULT_TIMEOUT_SEC = int(os.environ.get("PYCSL_SUPERVISOR_STEP_TIMEOUT", "600"))
_DEEP_MODE = os.environ.get("PYCSL_SUPERVISOR_DEEP", "0") == "1"

def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run git with strict args (never inject user-controlled paths
    without `--` separator). NEVER use --hard, -f, force-push, etc."""
    forbidden = {"--hard", "-f", "--force", "push", "commit",
                 "rebase", "clean"}
    for a in args:
        if a in forbidden:
            raise RuntimeError(
                f"_git: refusing forbidden arg {a!r} — supervisor "
                f"safety perimeter (1.4b)"
            )
    r = subprocess.run(
        ["git", *args],
        cwd=str(_PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if check and r.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} -> exit {r.returncode}\n"
            f"stderr: {r.stderr}"
        )
    return r


def _phase_tag(slug: str, phase_number: int) -> str:
    return f"feature-{slug}-phase-{phase_number}-start"



def _slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()[:64]


