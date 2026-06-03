from __future__ import annotations
import argparse, datetime, json, os, re, shutil, subprocess, sys
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
    '_snapshot_untracked_targets',
    '_rollback_phase',
    '_cleanup_phase_snapshot',
    '_delegate_model',
    '_DELEGATE_MAX_ATTEMPTS',
    '_PYCSL_SYNTAX_CHEAT',
]

# How many times the delegate may retry a phase, feeding the verifier's error
# back into the prompt each time (env-overridable; 1 disables retry).
_DELEGATE_MAX_ATTEMPTS = int(os.environ.get("PYCSL_SUPERVISOR_DELEGATE_ATTEMPTS", "3"))

# Concrete PyCSL contract-syntax rules injected into every delegate prompt.
# These encode the failure classes seen in practice (assigns-self syntax error,
# trusted-stripping leaving an unprovable body, callee arity mismatch) so the
# delegate avoids them up front and can recognise them in retry feedback.
_PYCSL_SYNTAX_CHEAT = r"""## PyCSL contract syntax — avoid these rejections
- `#@ assigns` takes LVALUES, never a bare object. Use `assigns \nothing` for a
  pure function, or name the mutated fields: `assigns self.count, self.items`.
  Writing `assigns self` is a SYNTAX ERROR (the parser expects `self.<field>`).
- STDLIB STUBS ARE BODY-VERIFIED — do NOT use `#@ \trusted`. The body must
  PROVABLY satisfy every `ensures`: `return 0` already proves `\result >= 0` /
  `== 0` / boolean `0|1`, so just omit `\trusted`. If `return 0` can't satisfy the
  contract (e.g. `ensures \result == x`), give a body that matches it (e.g.
  `return x`). For an irreducibly-opaque kernel (parsing, byte marshaling) call an
  abstract op and pin its `ensures` with a named `#@ proof rocq <Lemma>` /
  `#@ proof lean <Lemma>` citation — never `\trusted`. (Policy:
  config/skills/agent-stdlib-annotate/SKILL.md; lint: bin/check-no-trusted-stubs.py.)
- Call stub functions with EXACTLY the parameters they declare; an arity mismatch
  yields `int -> int, but is applied to N arguments`.
- The memory model is `hoare`: ints and `array int` are value-semantic (no heap).
"""

def _build_phase_prompt(phase: "Phase", plan_text: str,
                        prior_error: str = "") -> str:
    """Wrap the coding-LLM scaffold around the phase body + target file contents.

    `prior_error` (set on a retry) is shown prominently so the delegate corrects
    the exact verifier rejection from its previous attempt."""
    if not _CODING_LLM_PROMPT.is_file():
        scaffold = "(coding-llm-prompt.md missing; falling back to bare instructions)"
    else:
        scaffold = _CODING_LLM_PROMPT.read_text()

    # On a retry, lead with the previous failure so the model fixes exactly that.
    feedback = ""
    if prior_error:
        feedback = (
            "## YOUR PREVIOUS ATTEMPT FAILED — fix exactly this\n\n"
            "The verifier rejected your last output with:\n\n```\n"
            + prior_error.strip()
            + "\n```\n\n"
            "Produce a corrected full file (or diff) that resolves the above. "
            "Re-read the PyCSL contract-syntax rules below.\n\n---\n"
        )

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
        feedback,
        scaffold,
        "",
        _PYCSL_SYNTAX_CHEAT,
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


def _phase_snapshot_dir(slug: str, phase_number: int) -> Path:
    return _HALT_REPORT_ROOT / slug / ".rollback-snapshot" / f"phase-{phase_number}"


def _snapshot_untracked_targets(slug: str, phase_number: int,
                                target_files: list[str]) -> None:
    """Before a phase's delegate edits its targets, copy aside any target that
    EXISTS on disk but is NOT in HEAD (untracked / never committed).

    The per-phase rollback tag only captures *tracked* state, so without this
    `_rollback_phase` cannot tell a pre-existing untracked file from a
    delegate-created one and would delete it (data loss). Snapshotting lets the
    rollback restore such files instead. Tracked targets are already protected
    by the tag and are skipped."""
    snap_dir = _phase_snapshot_dir(slug, phase_number)
    shutil.rmtree(snap_dir, ignore_errors=True)
    for target in target_files:
        rel = target.lstrip("./").lstrip("/")
        in_head = _git("cat-file", "-e", f"HEAD:{rel}",
                       check=False).returncode == 0
        if in_head:
            continue
        src = _PROJECT_ROOT / rel
        if src.is_file():
            dst = snap_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def _cleanup_phase_snapshot(slug: str, phase_number: int) -> None:
    """Drop the per-phase untracked-target snapshot (transient, under metrics/).
    Called on delegation SUCCESS — the start tag is kept as an audit trail."""
    shutil.rmtree(_phase_snapshot_dir(slug, phase_number), ignore_errors=True)


def _rollback_phase(slug: str, phase_number: int,
                    target_files: list[str]) -> bool:
    """Revert per-phase targets to the per-phase start state. Returns success.

    Tracked targets are restored from the start tag. Targets absent from the tag
    are either pre-existing untracked files (restored from the phase-start
    snapshot — see `_snapshot_untracked_targets`) or genuinely delegate-created
    (deleted)."""
    tag = _phase_tag(slug, phase_number)
    # Check tag exists
    r = _git("rev-parse", "--verify", tag, check=False)
    if r.returncode != 0:
        return False
    snap_dir = _phase_snapshot_dir(slug, phase_number)
    for target in target_files:
        rel = target.lstrip("./").lstrip("/")
        existed = _git("cat-file", "-e", f"{tag}:{target}",
                       check=False).returncode == 0
        if existed:
            try:
                _git("restore", f"--source={tag}", "--worktree", "--staged",
                     "--", target)
            except RuntimeError:
                return False
        else:
            p = _PROJECT_ROOT / rel
            snap = snap_dir / rel
            if snap.is_file():
                # Pre-existing untracked file → restore it, never delete.
                try:
                    p.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(snap, p)
                except OSError:
                    return False
            else:
                # Genuinely created by the delegate → remove.
                try:
                    if p.is_file():
                        p.unlink()
                except OSError:
                    return False
                _git("rm", "-f", "--cached", "--ignore-unmatch", "--", target,
                     check=False)
    # Delete the tag + drop the snapshot (rollback complete)
    _git("tag", "-d", tag, check=False)
    shutil.rmtree(snap_dir, ignore_errors=True)
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


