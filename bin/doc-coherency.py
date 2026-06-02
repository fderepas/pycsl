#!/usr/bin/env python3
"""PyCSL documentation-coherency check.

Every ``#@`` directive defined in ``test-suite/annotations.md`` (the
canonical source) must appear in:

  1. ``README.md`` — contract-language quick-reference table
  2. ``test-suite/annotations.md`` — directive table + detail subsection
  3. ``docs/pycsl-concrete-syntax-reference.md`` — grammar production
  4. ``docs/pycsl-static-semantics-reference.md`` — well-formedness rule
  5. ``docs/pycsl-translational-reference.md`` — translation rule
                                                  (or explicit no-emission note)

This tool walks all five surfaces and reports drift. It is the
companion of ``bin/stdlib-coverage.py``, applied to the directive
catalogue rather than the stdlib API surface.

See ``config/skills/pycsl-doc-coherency/SKILL.md`` for the discipline,
and ``config/skills/pycsl-how-to-develop/SKILL.md`` §9 step 9 for the
per-PR workflow.

Modes:

  ``doc-coherency.py --list-directives``
        Print every directive name discovered in annotations.md.

  ``doc-coherency.py --check [directive]``
        Reconcile the directive (or all directives) against the four
        target surfaces. Exits 1 on any gap; 0 otherwise.

Exit codes:

  0  pass
  1  drift detected
  2  tool error
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parents[1]
README          = REPO_ROOT / "README.md"
ANNOTATIONS_MD  = REPO_ROOT / "test-suite" / "annotations.md"
CONCRETE_REF    = REPO_ROOT / "docs" / "pycsl-concrete-syntax-reference.md"
STATIC_SEM_REF  = REPO_ROOT / "docs" / "pycsl-static-semantics-reference.md"
TRANSLATIONAL_REF = REPO_ROOT / "docs" / "pycsl-translational-reference.md"

# Extreme Rigor acceptance-syntax coherency (gap 10): the user-facing
# reference doc must stay in sync with what the supervisor actually
# parses and forbids.
SUPERVISOR_PY    = REPO_ROOT / "src" / "pycsl" / "agents" / "agent-feature-supervisor.py"
# The supervisor was modularised: the gate-only entry above re-exports the
# acceptance machinery from this package, where the _FORBIDDEN_* sets now live.
SUPERVISOR_PKG   = REPO_ROOT / "src" / "pycsl" / "agents" / "feature_supervisor"
ACCEPTANCE_SYNTAX_MD = REPO_ROOT / "config" / "skills" / "csl-from-scratch" / \
    "references" / "acceptance-syntax.md"

# Predicate keywords the supervisor's `_ACCEPTANCE_BULLET_RE` accepts.
# Every one must be documented in acceptance-syntax.md.
_ACCEPTANCE_PREDICATES = ["exits", "stdout ==", "stdout >=", "stdout matches"]

TARGETS: List[Tuple[str, Path]] = [
    ("README",          README),
    ("annotations.md",  ANNOTATIONS_MD),
    ("concrete-syntax", CONCRETE_REF),
    ("static-semantics", STATIC_SEM_REF),
    ("translational",   TRANSLATIONAL_REF),
]


# ----------------------------------------------------------------------
# Directive extraction
# ----------------------------------------------------------------------
# `test-suite/annotations.md` is the canonical source. We extract
# directive names from two patterns:
#
#   Table rows like: `#@ requires <expr>`
#   Backslash-prefixed forms: `\diverges`, `\trusted`, `\variant`
#
# We then exclude well-known non-directive matches (`#@ proof rocq:` is
# the colon-suffixed deprecated form; the canonical is `#@ proof`).

# Patterns matched in annotations.md
_DIRECTIVE_PAT = re.compile(
    r"`#@\s+(\\?[a-z_][a-z_0-9]*)\b"
)

# Hand-curated allowlist for directives whose canonical form differs
# from the simple `#@ name` pattern (e.g. `no_exception \all`).
_KNOWN_ALIASES: Dict[str, List[str]] = {
    # canonical name → alternate forms accepted in any surface
    "no_exception": ["no_exception", r"no_exception\s+\\all"],
    "ghost":        ["ghost"],
    "loop":         ["loop invariant", "loop variant"],
    "class":        ["class invariant"],
    "assumes":      ["assumes bounded_int", "assumes"],
    "proof":        ["proof rocq", "proof lean", "proof"],
}

# Stop-words that the simple regex would over-match (English words used
# as `#@ <word>` in prose).
_STOPWORDS: set = {
    "annotation", "annotations", "lines", "the", "see", "by",
}


def extract_directives_from_annotations() -> List[str]:
    """Return the canonical directive list from
    ``test-suite/annotations.md`` — every distinct ``#@ <name>`` form,
    deduplicated and sorted."""
    if not ANNOTATIONS_MD.exists():
        print(f"[!] Canonical source missing: {ANNOTATIONS_MD.relative_to(REPO_ROOT)}",
              file=sys.stderr)
        return []
    raw = ANNOTATIONS_MD.read_text()
    out: set = set()
    for m in _DIRECTIVE_PAT.finditer(raw):
        name = m.group(1)
        if name in _STOPWORDS:
            continue
        out.add(name)
    return sorted(out)


# ----------------------------------------------------------------------
# Coverage check
# ----------------------------------------------------------------------

def _patterns_for(directive: str) -> List[str]:
    """Return a list of regex patterns that count as "directive
    present" in any surface.

    The strategy is two-tier:

    1. **Strong signals** (high precision): the directive appears as
       ``#@ <name>``, as ``<name>_decl`` (EBNF production), as
       ``<Directive>Decl`` (CSL AST node class), or inside a backtick
       phrase that starts with the directive name.
    2. **Boundary form** (`name\\b` for distinctive multi-syllable
       directives that are unlikely to collide with English prose):
       used as a last-resort acceptance.

    Single-syllable directives that overlap with English prose
    (``class``, ``label``, ``loop``, ``ghost``) only accept the strong
    signals; the boundary form is suppressed for them via the
    ``_DISTINCTIVE`` allowlist.
    """
    aliases = _KNOWN_ALIASES.get(directive, [directive])
    pats: List[str] = []
    for alias in aliases:
        # Strip leading backslash so the regex matches `\diverges`
        # whether it's written `\\diverges` or `diverges` in the doc.
        bare = alias.lstrip("\\")
        # Strong signal 1 — `#@ <directive>`.
        pats.append(rf"#@\s*\\?{re.escape(bare)}\b")
        # Strong signal 2 — grammar production.
        pats.append(rf"{re.escape(bare)}_decl\b")
        # Strong signal 3 — CSL node class.
        cls = "".join(p.capitalize() for p in bare.split("_"))
        pats.append(rf"{cls}Decl\b")
        # Strong signal 4 — backtick phrase starting with the
        # directive: ``\`<directive>...\``` or ``\`(\\<directive>...\```.
        if alias.startswith("\\"):
            pats.append(rf"`\\\\?{re.escape(bare)}\b")
        else:
            pats.append(rf"`{re.escape(bare)}\b")
        # Strong signal 5 — TeX-formatted directive in a translation
        # rule, e.g. ``\texttt{\#@ <directive> ...}``.
        pats.append(rf"\\texttt\{{[^}}]*\\?#@\s*\\?{re.escape(bare)}")
        # Boundary form for distinctive identifiers only.
        if alias in _DISTINCTIVE or (alias.startswith("\\")):
            pats.append(rf"\b\\?{re.escape(bare)}\b")
    return pats


# Directives whose bare name is distinctive enough to accept as a
# coverage signal without further context. Single-syllable English
# words (``class``, ``label``, ``loop``, ``ghost``) are excluded —
# they require a strong-signal match.
_DISTINCTIVE: set = {
    "requires", "ensures", "assigns", "raises", "assumes",
    "diverges", "trusted", "variant",
    "no_exception", "allow_finalizer", "allow_iteration_mutation",
    "mutex_invariant", "lock_order", "thread_entry",
    "acquires", "releases", "critical", "shared", "protected_by",
    "proof",
}


def directive_present(directive: str, path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text()
    for pat in _patterns_for(directive):
        if re.search(pat, text):
            return True
    return False


def check(directives: Optional[List[str]] = None) -> int:
    if directives is None:
        directives = extract_directives_from_annotations()
        if not directives:
            return 2
    print(f"=== Doc-coherency check ({len(directives)} directive(s)) ===")
    rc = 0
    max_name = max(len(d) for d in directives) if directives else 8
    header = "directive".ljust(max_name + 2) + \
             "".join(label.ljust(18) for label, _ in TARGETS)
    print(header)
    print("-" * len(header))
    for d in directives:
        row = d.ljust(max_name + 2)
        missing: List[str] = []
        for label, path in TARGETS:
            present = directive_present(d, path)
            row += ("✓".ljust(18) if present else "MISSING".ljust(18))
            if not present:
                missing.append(label)
        print(row)
        if missing:
            rc = 1
    if rc != 0:
        print("")
        print("[!] One or more directives are missing from a normative surface.")
        print("    Update the surfaces and re-run, or skip the gate with")
        print("    PYCSL_SKIP_DOC_COHERENCY_CHECK=1.")
    else:
        print("")
        print("[+] All directives present in every normative surface.")
    return rc


# ----------------------------------------------------------------------
# Acceptance-syntax coherency (Extreme Rigor — gap 10)
# ----------------------------------------------------------------------
# `acceptance-syntax.md` is the user-facing reference for ER plan
# authors. It documents the predicate shapes the supervisor accepts and
# the tokens it refuses to execute. If the supervisor's implementation
# drifts from the doc (a new forbidden token, a removed predicate) — or
# someone edits the doc and drops a rule — an author can't trust it.
#
# This check parses the supervisor source with `ast` (no import, no
# side effects) to read the live `_FORBIDDEN_*` collections and the
# predicate keywords, then asserts each is documented. It is the
# acceptance-block analogue of the directive-coverage check above.

def _supervisor_forbidden_sets() -> Dict[str, List[str]]:
    """AST-extract the supervisor's forbidden token/separator/prefix
    collections. Returns {} (and prints) on any parse failure.

    Scans the gate-only entry AND the feature_supervisor/ package modules
    (the modularisation moved the _FORBIDDEN_* sets into the package), so the
    check survives wherever within the package they are defined."""
    sources = [SUPERVISOR_PY]
    if SUPERVISOR_PKG.is_dir():
        sources.extend(sorted(SUPERVISOR_PKG.glob("*.py")))
    sources = [p for p in sources if p.exists()]
    if not sources:
        print(f"[!] Supervisor source missing: "
              f"{SUPERVISOR_PY.relative_to(REPO_ROOT)}", file=sys.stderr)
        return {}
    want = {"_FORBIDDEN_TOKENS", "_FORBIDDEN_SEPARATORS",
            "_FORBIDDEN_PREFIXES"}
    out: Dict[str, List[str]] = {}
    for src in sources:
        tree = ast.parse(src.read_text())
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id in want and t.id not in out:
                        val = ast.literal_eval(node.value)
                        out[t.id] = sorted(val) if isinstance(
                            val, (set, frozenset)) else list(val)
    return out


def check_acceptance_syntax() -> int:
    """Reconcile acceptance-syntax.md against the supervisor's parser
    and safety classifier. Exits 1 on drift; 0 otherwise."""
    print("=== Acceptance-syntax coherency (ER gap 10) ===")
    if not ACCEPTANCE_SYNTAX_MD.exists():
        print(f"[!] Reference doc missing: "
              f"{ACCEPTANCE_SYNTAX_MD.relative_to(REPO_ROOT)}", file=sys.stderr)
        return 2
    forbidden = _supervisor_forbidden_sets()
    if not forbidden:
        return 2
    doc = ACCEPTANCE_SYNTAX_MD.read_text()
    rc = 0

    # 1. Every code-enforced predicate keyword must be documented.
    for kw in _ACCEPTANCE_PREDICATES:
        if kw in doc:
            print(f"  ✓ predicate documented: {kw!r}")
        else:
            print(f"  MISSING predicate in doc: {kw!r}")
            rc = 1

    # 2. Every code-enforced forbidden token/separator/prefix must be
    #    documented so an author knows it will be rejected.
    enforced: List[str] = []
    for key in ("_FORBIDDEN_TOKENS", "_FORBIDDEN_SEPARATORS",
                "_FORBIDDEN_PREFIXES"):
        enforced.extend(forbidden.get(key, []))
    for tok in enforced:
        # Match the token as a word in the prose (tokens like `gh pr `
        # carry trailing space; strip for the search).
        needle = tok.strip()
        if needle in doc:
            print(f"  ✓ forbidden rule documented: {needle!r}")
        else:
            print(f"  MISSING forbidden rule in doc: {needle!r} "
                  f"(supervisor rejects it; doc must warn authors)")
            rc = 1

    if rc:
        print("")
        print("[!] acceptance-syntax.md has drifted from the supervisor.")
        print("    Update config/skills/csl-from-scratch/references/"
              "acceptance-syntax.md")
        print("    (or the supervisor) so the two agree, then re-run.")
    else:
        print("")
        print("[+] acceptance-syntax.md is in sync with the supervisor.")
    return rc


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="PyCSL documentation-coherency check.")
    sub = parser.add_subparsers(dest="mode", required=True)

    sub.add_parser("--list-directives".lstrip("-"),
                    help="Print every directive discovered in annotations.md.")

    p_check = sub.add_parser("--check".lstrip("-"),
                              help="Reconcile each directive against the "
                                   "five normative surfaces (also runs the "
                                   "acceptance-syntax coherency check).")
    p_check.add_argument("directive", nargs="?", default=None,
                         help="Check a single directive (default: all).")

    sub.add_parser("--check-acceptance-syntax".lstrip("-"),
                    help="Reconcile acceptance-syntax.md against the "
                         "supervisor's parser + safety classifier.")

    if argv is None:
        argv = sys.argv[1:]
    argv = [a.lstrip("-") if a.startswith("--") and a in
            ("--list-directives", "--check", "--check-acceptance-syntax")
            else a for a in argv]
    args = parser.parse_args(argv)

    if args.mode == "list-directives":
        for d in extract_directives_from_annotations():
            print(d)
        return 0

    if args.mode == "check":
        targets = [args.directive] if args.directive else None
        rc = check(targets)
        # A full `--check` run also gates the ER acceptance-syntax doc.
        # A single-directive query stays narrowly scoped.
        if not args.directive:
            print("")
            rc = check_acceptance_syntax() or rc
        return rc

    if args.mode == "check-acceptance-syntax":
        return check_acceptance_syntax()

    return 2


if __name__ == "__main__":
    sys.exit(main())
