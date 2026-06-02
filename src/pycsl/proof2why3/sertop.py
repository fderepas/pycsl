"""sertop / coq-serapi subprocess driver (proof2why3 Phase A — sticky-02.md).

Production driver replacing the v0 foundation. Spawns sertop as a
long-lived subprocess, sends tagged commands, reads tagged responses,
and exposes a `type_of(qualname)` API that returns the elaborated
`CoqConstr` s-expression for a cited theorem.

Protocol (SerAPI 8.20.0+0.20.0):

  1. We write `(Add () "<vernac>.")` followed by `(Exec <tag>)` to load
     a module (e.g. `Require Import gcd`).
  2. We write `(Query () (TypeOf "<qualname>"))` to request the
     elaborated type of a named global.
  3. sertop emits:
       (Answer <N> Ack)
       (Feedback ...) *               # ignored
       (Answer <N> (ObjList ((CoqConstr <constr_sexp>))))
       (Answer <N> Completed)
     We read until `Answer N Completed`, capturing the `ObjList`
     payload along the way.

  4. The returned `constr_sexp` is fed into `from_sexp.project_to_ir`
     to produce a shared-IR `Term`.

The Coq `Constr.t` schema (per Coq 8.20 +
`~/.opam/coq-4.14/.opam-switch/sources/coq-serapi.../serlib_8_20/ser_constr.ml`):

  Constr.t ::= Rel of int                                  ; de Bruijn index
             | Var of Id.t                                  ; free var
             | Sort of Sorts.t                              ; universe
             | Cast of Constr.t * cast_kind * Constr.t      ; type ascription
             | Prod of binder_annot * Constr.t * Constr.t   ; ∀
             | Lambda of binder_annot * Constr.t * Constr.t ; λ
             | LetIn of binder_annot * Constr.t * Constr.t * Constr.t
             | App of Constr.t * Constr.t array             ; n-ary application
             | Const of Constant.t * Univ.Instance.t        ; named global const
             | Ind of inductive * Univ.Instance.t           ; type constructor
             | Construct of constructor * Univ.Instance.t   ; data constructor
             | Case ...
             | Fix ...
             | CoFix ...
             | Proj of Projection.t * Constr.t
             | Int of Uint63.t
             | Float of Float64.t
             | Array of ...

For type extraction the cases we need are Prod, Rel, App, Const, Ind,
Construct (for nat O / S literals). The others (Lambda, LetIn, Case,
Fix, Cast, Proj, Int, Float, Array) fall through to `Unsupported` at
the IR level.

This module supplies:
  - `SertopSession` — context-managed subprocess wrapper.
  - `extract_via_sertop(proof_file, qualnames) -> dict[qualname,
     constr_sexp]` — the production extractor.
  - `parse_sexp` / s-expression utilities (also imported by
    `from_sexp.py`).
"""
from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple


def sertop_available() -> bool:
    """True iff sertop is on $PATH (post `opam install coq-serapi`)."""
    return shutil.which("sertop") is not None


def sertop_version() -> str:
    """Return sertop's reported version, or 'unknown' if unavailable."""
    if not sertop_available():
        return "unavailable"
    try:
        out = subprocess.run(
            ["sertop", "--version"], capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip().splitlines()[0]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "unknown"


# ---------------------------------------------------------------------------
# Minimal s-expression reader/writer
# ---------------------------------------------------------------------------


def _sexp_tokens(s: str) -> Iterator[str]:
    """Tokenize an s-expression string: emit '(', ')', and atoms.

    Quoted atoms (`"..."`) are returned with the quotes preserved so
    downstream parsing can distinguish them from bare identifiers.
    """
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
            continue
        if c == "(":
            yield "("
            i += 1
            continue
        if c == ")":
            yield ")"
            i += 1
            continue
        if c == '"':
            j = i + 1
            while j < n and s[j] != '"':
                if s[j] == "\\":
                    j += 2
                    continue
                j += 1
            yield s[i:j + 1]
            i = j + 1
            continue
        j = i
        while j < n and not s[j].isspace() and s[j] not in "()":
            j += 1
        yield s[i:j]
        i = j


def _sexp_parse(tokens: List[str]) -> object:
    """Parse a token list into nested tuples (atoms remain strings)."""
    if not tokens:
        raise ValueError("empty s-expression")
    tok = tokens.pop(0)
    if tok == "(":
        out: List[object] = []
        while tokens and tokens[0] != ")":
            out.append(_sexp_parse(tokens))
        if not tokens:
            raise ValueError("unterminated list in s-expression")
        tokens.pop(0)  # consume ')'
        return tuple(out)
    if tok == ")":
        raise ValueError("unexpected ')' in s-expression")
    return tok


def parse_sexp(s: str) -> object:
    """Parse a single top-level s-expression from `s`."""
    tokens = list(_sexp_tokens(s))
    return _sexp_parse(tokens)


# ---------------------------------------------------------------------------
# SertopSession: long-lived subprocess driver
# ---------------------------------------------------------------------------


def _process_sertop_line(line: str,
                          payloads_by_tag: Dict[int, object]) -> Optional[int]:
    """Parse one sertop output line. On `ObjList` capture the payload
    by tag. Return the tag iff the line is `(Answer <tag> Completed)`,
    else None."""
    if not line.startswith("(Answer"):
        return None
    try:
        sexp = parse_sexp(line)
    except (ValueError, IndexError):
        return None
    if not isinstance(sexp, tuple) or len(sexp) < 3:
        return None
    if sexp[0] != "Answer":
        return None
    try:
        ans_tag = int(sexp[1])
    except (ValueError, TypeError):
        return None
    body = sexp[2]
    if body == "Completed":
        return ans_tag
    if isinstance(body, tuple) and body and body[0] == "ObjList" and len(body) >= 2:
        payloads_by_tag[ans_tag] = body[1]
    return None


def _extract_stmid(added_payload: object) -> Optional[int]:
    """Parse the STMID out of an `(Added <stmid> ...)` Answer body.

    sertop's `Add` returns `(Answer N (Added STMID (...))) NewAddTip`
    style; we want the STMID."""
    if not isinstance(added_payload, tuple) or len(added_payload) < 2:
        return None
    if added_payload[0] != "Added":
        return None
    try:
        return int(added_payload[1])
    except (ValueError, TypeError):
        return None


def run_sertop_batch(load_paths,
                      cwd: Path,
                      require_module: str,
                      qualnames: List[str],
                      timeout_s: float = 60.0,
                      require_prefix: Optional[str] = None) -> Dict[str, object]:
    """One-shot batch invocation of sertop.

    Sends `(Add () "Require Import <require_module>.")`, then the
    matching `(Exec <stmid>)`, then `(Query () (TypeOf "qn"))` per
    qualname — all up front. Reads responses until all expected
    Answer tags reach Completed. Returns
    `{qualname: constr_sexp}`.

    The batch pattern is needed because sertop's output stream is
    buffered: individual commands' Completed messages don't reach the
    reader until later commands are sent. Batching all commands
    upfront eliminates the deadlock.
    """
    args = ["sertop", "--printer=sertop"]
    for entry in load_paths:
        # Accept either Path or (Path, logical_name) tuple. Empty
        # logical_name imports under the file-stem-as-module convention.
        if isinstance(entry, tuple):
            path, logical = entry
            args += ["-Q", f"{path},{logical}"]
        else:
            args += ["-Q", f"{entry},"]
    if not load_paths:
        args += ["-Q", ".,"]
    proc = subprocess.Popen(
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(cwd),
        bufsize=1,
    )

    # Send all commands. Tag conventions:
    #   tag 0 → Add (Require Import)
    #   tag 1 → Exec (uses STMID from Add response)
    #   tag 2..2+n-1 → Query TypeOf per qualname
    if require_prefix:
        cmds = [f'(Add () "From {require_prefix} Require Import {require_module}.")']
    else:
        cmds = [f'(Add () "Require Import {require_module}.")']
    # We don't know the STMID yet, but sertop will return Added with it.
    # Since we batch send, we need to know STMID before sending Exec.
    # Workaround: send Add, then Exec with a guess (Add always returns
    # a fresh STMID; for a single Add the value is deterministic — 2
    # — because sertop's internal counter starts at 1 for the Init,
    # then 2 for the first user Add). This works in practice for
    # this batch pattern; if it fails we'd see Exec error.
    cmds.append("(Exec 2)")
    for qn in qualnames:
        cmds.append(f'(Query () (TypeOf "{qn}"))')
    # Trailing flush. sertop's output buffer holds the last
    # response's Completed line until another command is sent;
    # `(Quit)` forces the flush and tells sertop to shut down
    # gracefully after producing all pending output.
    cmds.append("(Quit)")

    # Pipeline all commands then use communicate() to read everything
    # until sertop exits (triggered by the trailing (Quit) command).
    # This avoids select/read-buffering races: communicate() blocks
    # until EOF and returns the complete stdout.
    assert proc.stdin is not None
    all_input = "\n".join(cmds) + "\n"
    try:
        stdout_data, _stderr_data = proc.communicate(
            input=all_input, timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout_data = ""

    payloads_by_tag: Dict[int, object] = {}
    for line in stdout_data.splitlines():
        _process_sertop_line(line.strip(), payloads_by_tag)

    # Map per-qualname: query tags start at 2.
    out: Dict[str, object] = {}
    for i, qn in enumerate(qualnames):
        tag = 2 + i
        if tag not in payloads_by_tag:
            continue
        payload = payloads_by_tag[tag]
        if isinstance(payload, tuple):
            for elem in payload:
                if (isinstance(elem, tuple) and len(elem) == 2
                        and elem[0] == "CoqConstr"):
                    out[qn] = elem[1]
                    break
    return out


# Legacy SertopSession is kept for callers that want a long-lived
# session; the batch helper above is the production path.
@dataclass
class SertopSession:
    """Convenience wrapper for callers that need a long-lived session.

    Internally delegates to `run_sertop_batch` for each query group
    (which restarts sertop per group). For multi-query scenarios
    `run_sertop_batch` is more efficient."""
    load_paths: List[Path] = field(default_factory=list)
    cwd: Optional[Path] = None
    proc: Optional[subprocess.Popen] = None  # for compat with v0 callers
    seq: int = 0

    def __enter__(self) -> "SertopSession":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    def type_of_batch(self, require_module: str,
                       qualnames: List[str]) -> Dict[str, object]:
        cwd = self.cwd or Path.cwd()
        return run_sertop_batch(self.load_paths, cwd, require_module, qualnames)


# ---------------------------------------------------------------------------
# Top-level entry, integrated with extract.py via env var
# ---------------------------------------------------------------------------


def extract_via_sertop(proof_file: Path,
                       qualnames: List[str]) -> Dict[str, object]:
    """Extract elaborated theorem types via sertop.

    Returns `{qualname: constr_sexp}` where `constr_sexp` is the raw
    parsed s-expression of the elaborated Constr.t. The caller is
    expected to project via `from_sexp.project_to_ir`.

    Returns an empty dict when sertop isn't available or the env var
    `PROOF2WHY3_USE_SERTOP` isn't set to `1` — callers must then fall
    back to the coqc-Check extractor.
    """
    if not sertop_available():
        return {}
    if os.environ.get("PROOF2WHY3_USE_SERTOP", "") != "1":
        return {}
    proof_file = proof_file.resolve()  # absolute path required
    proof_dir = proof_file.parent
    module_name = proof_file.stem  # e.g., "gcd"
    # Compile the .v file first so the .vo exists.
    subprocess.run(
        ["coqc", "-R", str(proof_dir), "", proof_file.name],
        cwd=str(proof_dir), capture_output=True, text=True, timeout=180,
    )
    return run_sertop_batch(
        load_paths=[proof_dir],
        cwd=proof_dir,
        require_module=module_name,
        qualnames=qualnames,
    )
