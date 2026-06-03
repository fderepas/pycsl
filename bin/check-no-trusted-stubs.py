#!/usr/bin/env python3
"""Lint: standard-library stubs must be body-verified (no `#@ \trusted`).

Policy: config/skills/agent-stdlib-annotate/SKILL.md — stdlib stubs under
src/pycsl_lib/ carry ZERO `\trusted`; an irreducibly-opaque kernel uses an
abstract `val` + a named `#@ proof rocq/lean` citation instead.

Modes:
  (default)            Census — list every `\trusted` under src/pycsl_lib/ and
                       exit 0 (informational; the ~270 generated stubs are being
                       migrated, so tree-wide is not yet a hard gate).
  --strict FILE...     Hard-fail (exit 1) if any of the named files contains
                       `\trusted`. Use on a stub once it has been migrated, and
                       in CI for the phase's target stubs.

Usage:
  bin/check-no-trusted-stubs.py
  bin/check-no-trusted-stubs.py --strict src/pycsl_lib/io.py src/pycsl_lib/ast.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STUB_ROOT = REPO_ROOT / "src" / "pycsl_lib"
_TRUSTED_RE = re.compile(r"^\s*#@\s*\\trusted\b", re.M)


def trusted_hits(py: Path) -> list[int]:
    """Line numbers (1-based) of `#@ \trusted` directives in a file."""
    try:
        text = py.read_text(errors="replace")
    except OSError:
        return []
    return [text.count("\n", 0, m.start()) + 1 for m in _TRUSTED_RE.finditer(text)]


def _iter_stubs() -> list[Path]:
    return sorted(p for p in STUB_ROOT.rglob("*.py") if "__pycache__" not in p.parts)


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--strict":
        targets = [Path(a) if Path(a).is_absolute() else REPO_ROOT / a
                   for a in argv[1:]]
        bad = False
        for t in targets:
            hits = trusted_hits(t)
            if hits:
                bad = True
                rel = t.relative_to(REPO_ROOT) if t.is_relative_to(REPO_ROOT) else t
                print(f"[check-no-trusted-stubs] FAIL {rel}: "
                      f"`#@ \\trusted` at line(s) {', '.join(map(str, hits))}")
            else:
                print(f"[check-no-trusted-stubs] OK {t.name}: 0 trusted")
        if bad:
            print("  Policy: stdlib stubs are body-verified — replace `\\trusted` "
                  "with a body proof or an abstract `val` + `#@ proof rocq/lean` "
                  "citation (agent-stdlib-annotate skill).")
            return 1
        return 0

    # Default: informational census.
    if not STUB_ROOT.is_dir():
        print(f"[check-no-trusted-stubs] no stub root at {STUB_ROOT}")
        return 0
    total = 0
    files = 0
    for py in _iter_stubs():
        hits = trusted_hits(py)
        if hits:
            files += 1
            total += len(hits)
            print(f"  {py.relative_to(REPO_ROOT)}: {len(hits)} `\\trusted`")
    print(f"[check-no-trusted-stubs] census: {total} `\\trusted` directive(s) "
          f"across {files} stub file(s) under src/pycsl_lib/ "
          f"(migration target → 0; use --strict <file> to gate a migrated stub).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
