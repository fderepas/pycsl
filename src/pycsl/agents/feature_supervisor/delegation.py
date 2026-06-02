from __future__ import annotations
import argparse, datetime, json, os, re, subprocess, sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from ._common import *
from .competency import *

__all__ = [
    '_build_phase_prompt',
    '_DIFF_FENCE_RE',
    '_extract_diff',
    '_apply_diff',
    '_FILE_BLOCK_RE',
    '_FENCE_RE',
    'FILE_OUTPUT_INSTRUCTION',
    '_extract_files',
    '_write_files',
    '_rollback_phase',
    '_delegate_model',
]

def _build_phase_prompt(phase: "Phase", plan_text: str) -> str:
    """Wrap the coding-LLM scaffold around the phase body + target file contents."""
    if not _CODING_LLM_PROMPT.is_file():
        scaffold = "(coding-llm-prompt.md missing; falling back to bare instructions)"
    else:
        scaffold = _CODING_LLM_PROMPT.read_text()

    # Prepend the supervisor persona so a delegate inherits the ER
    # discipline (gap 11). Best-effort: skip silently if absent.
    persona = ""
    if _AGENT_DESCRIPTION.is_file():
        persona = (
            "## Operate under this persona (agent-feature-supervisor)\n\n"
            + _AGENT_DESCRIPTION.read_text()
            + "\n\n---\n\n"
        )

    # Inject the skills this phase's role needs (competency matrix), as direct
    # text — the role-appropriate knowledge for the delegate.
    skills_block = ""
    level = _phase_level(phase)
    role = _phase_role(phase)
    role_tag = (level or "—") + (f"/{role}" if role else "")
    skill_names = _phase_competency_skills(phase, _load_competency_matrix())
    if skill_names:
        chunks = [f"## Skills for your role ({role_tag})\n"]
        for name in skill_names:
            sk = _SKILLS_ROOT / name / "SKILL.md"
            if sk.is_file():
                chunks.append(f"### Skill: {name}\n\n{sk.read_text()}\n\n---\n")
        skills_block = "\n".join(chunks) + "\n"

    parts = [
        persona,
        scaffold,
        "",
        "---",
        "",
        skills_block,
        f"## This phase: Phase {phase.number} — {phase.title}",
        "",
        "### Phase body (from the feature plan)",
        "",
        phase.raw_body,
        "",
        "### Target files (current contents)",
        "",
    ]
    for target in phase.target_files:
        p = _PROJECT_ROOT / target.lstrip("./").lstrip("/")
        if p.is_file():
            try:
                content = p.read_text()
            except UnicodeDecodeError:
                content = "(binary file; not inlined)"
        elif p.is_dir():
            content = "(directory target; list its contents in your diff)"
        else:
            content = "(file does not yet exist; create it in your diff)"
        parts.append(f"#### `{target}`")
        parts.append("")
        parts.append("```")
        parts.append(content)
        parts.append("```")
        parts.append("")
    parts.append("---")
    parts.append("")
    parts.append(FILE_OUTPUT_INSTRUCTION)
    return "\n".join(parts)


_DIFF_FENCE_RE = re.compile(
    r"```(?:diff)?\s*\n(.*?)\n```", re.S | re.I
)


def _extract_diff(llm_output: str) -> Optional[str]:
    """Find the first fenced diff block. None if absent."""
    m = _DIFF_FENCE_RE.search(llm_output)
    if not m:
        return None
    body = m.group(1)
    # Trim a leading `# refuse:` comment marker — treat as no diff.
    if body.strip().startswith("# refuse:"):
        return None
    return body


def _apply_diff(diff_text: str) -> tuple[bool, str]:
    """Validate + apply a unified diff. Returns (success, stderr-text)."""
    # The fenced-block extractor drops the trailing newline before the closing
    # ``` — git then reports "corrupt patch" on the unterminated last line.
    # Normalise to a single terminating newline before applying.
    if diff_text and not diff_text.endswith("\n"):
        diff_text += "\n"
    # First validate with --check so we don't mutate the tree on garbage
    r = subprocess.run(
        ["git", "apply", "--check", "--whitespace=nowarn", "--recount", "-"],
        cwd=str(_PROJECT_ROOT),
        input=diff_text,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return False, f"git apply --check failed:\n{r.stderr}"
    # Apply for real
    r = subprocess.run(
        ["git", "apply", "--whitespace=nowarn", "--recount", "-"],
        cwd=str(_PROJECT_ROOT),
        input=diff_text,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        return False, f"git apply failed:\n{r.stderr}"
    return True, ""


# Full-file output contract — far more robust than a unified diff for an
# LLM, which cannot reliably reproduce exact hunk context / line counts. The
# delegate emits the COMPLETE contents of each created/modified file between
# these markers; the supervisor writes the files directly (no patch parsing).
_FILE_BLOCK_RE = re.compile(
    r"^[ \t]*\*\*\* BEGIN FILE:[ \t]*(?P<path>.+?)[ \t]*\*\*\*[ \t]*\n"
    r"(?P<body>.*?)\n[ \t]*\*\*\* END FILE \*\*\*",
    re.S | re.M,
)
_FENCE_RE = re.compile(r"^```[A-Za-z0-9_-]*\n(.*)\n```\s*$", re.S)

FILE_OUTPUT_INSTRUCTION = (
    "## Output format (REQUIRED)\n\n"
    "Output the COMPLETE final contents of every file you create or modify — "
    "NOT a diff. Wrap each file EXACTLY like this, one block per file:\n\n"
    "*** BEGIN FILE: <repo-relative/path.py> ***\n"
    "<the entire file content, verbatim, with no surrounding code fence>\n"
    "*** END FILE ***\n\n"
    "Emit the full content even for a one-line change. Do not abbreviate, do "
    "not use `...`, do not emit a unified diff."
)


def _extract_files(llm_output: str) -> List[Tuple[str, str]]:
    """Extract (path, full-content) pairs from BEGIN/END FILE markers."""
    out: List[Tuple[str, str]] = []
    for m in _FILE_BLOCK_RE.finditer(llm_output):
        body = m.group("body")
        fence = _FENCE_RE.match(body.strip())
        if fence:  # tolerate an accidental code fence around the content
            body = fence.group(1)
        out.append((m.group("path").strip(), body))
    return out


def _write_files(pairs: List[Tuple[str, str]]) -> Tuple[bool, str, List[str]]:
    """Write each (repo-relative path, content). Returns (ok, err, written)."""
    written: List[str] = []
    repo = _PROJECT_ROOT.resolve()
    for rel, content in pairs:
        rel = rel.strip().lstrip("./").lstrip("/")
        target = (_PROJECT_ROOT / rel).resolve()
        try:
            target.relative_to(repo)  # refuse `..`/absolute escapes
        except ValueError:
            return False, f"refusing to write outside repo: {rel!r}", written
        if content and not content.endswith("\n"):
            content += "\n"
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content)
        except OSError as e:
            return False, f"write failed for {rel!r}: {e}", written
        written.append(rel)
    return True, "", written


def _rollback_phase(slug: str, phase_number: int,
                    target_files: list[str]) -> bool:
    """Revert per-phase targets to the per-phase start tag. Returns success."""
    tag = _phase_tag(slug, phase_number)
    # Check tag exists
    r = _git("rev-parse", "--verify", tag, check=False)
    if r.returncode != 0:
        return False
    # Restore each target. Files that existed at the tag are restored; files
    # the delegate newly CREATED (absent at the tag — common with full-file
    # output) are deleted, since `git restore` can't revert a non-existent
    # path.
    for target in target_files:
        existed = _git("cat-file", "-e", f"{tag}:{target}",
                       check=False).returncode == 0
        if existed:
            try:
                _git("restore", f"--source={tag}", "--worktree", "--staged",
                     "--", target)
            except RuntimeError:
                return False
        else:
            p = _PROJECT_ROOT / target.lstrip("./").lstrip("/")
            try:
                if p.is_file():
                    p.unlink()
            except OSError:
                return False
            _git("rm", "-f", "--cached", "--ignore-unmatch", "--", target,
                 check=False)
    # Delete the tag (rollback complete)
    _git("tag", "-d", tag, check=False)
    return True


def _delegate_model() -> str:
    """Model used for LLM delegation.

    Resolution order: `PYCSL_LLM_MODEL` env var → `model` key of
    `config/agents-config.json` → a safe Copilot default. A `claude-*`/`gpt-*`
    name routes to the GitHub Copilot CLI; any other name is treated as an
    Ollama tag (HTTP). Previously the delegate read only the env var and
    defaulted to "" — which mis-routed to the (possibly down) Ollama host.
    """
    env = os.environ.get("PYCSL_LLM_MODEL")
    if env:
        return env
    try:
        import json as _json
        cfg = _json.loads(
            (_PROJECT_ROOT / "config" / "agents-config.json").read_text())
        if cfg.get("model"):
            return cfg["model"]
    except Exception:
        pass
    return "claude-sonnet-4.6"


