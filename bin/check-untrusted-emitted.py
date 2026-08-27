#!/usr/bin/env python3
"""check-untrusted-emitted.py — INTEGRITY GATE for the self-annotation count.

THE HAZARD THIS CLOSES. Removing a `#@ \trusted` marker is what the TCB-reduction
campaign counts as a conversion. But removing the marker does NOT by itself guarantee
that anything is verified in its place: PyCSL has an AUTO-TRUST SAFETY VALVE, so a body
the emitter cannot lower is silently re-abstracted to an opaque `val` — and the file
still type-checks (L3-tc ✓) and still proves. A stub in that state has had its marker
removed while NOTHING about it is verified: the count improves, the TCB does not.

Discovered 2026-08-27 (relaunch #3) while probing candidate conversions: of 17 candidates
that passed L3-tc after their marker was dropped, **not one** was emitted as a definition
— 6 were dropped from emission entirely and 11 came back as abstract `val`s. L3-tc alone
is therefore NOT a conversion criterion.

WHAT THIS CHECKS. For every mirror function that is neither `#@ \trusted` nor
`#@ \abstract`, emit its file and require the function to appear as a real DEFINITION —
`let` / `let rec` / `let function` / … or a `with` continuation of a mutual-recursion
group (which is a definition with a body, not a `val`). Report:

    LET     - genuinely defined, body emitted        (the only healthy outcome)
    VAL     - silently re-abstracted                 (**the defect this gate exists for**)
    ABSENT  - not emitted as a standalone function

ABSENT is EXPECTED for `__init__` (constructors are inlined into the record's `by`
witness) and for dunders the emitter models structurally; those are allow-listed below by
SHAPE, not by name, so a new one is surfaced rather than hidden.

BASELINE at the time of writing: 687 un-trusted functions, **0 VAL**, and every ABSENT an
`__init__` / `_Tok.__repr__`. The campaign's booked conversions are clean — the count is
NOT inflated by silent re-abstraction.

Usage:  bin/check-untrusted-emitted.py [path-prefix ...]
Exit 1 if any VAL is found, or any unexpected ABSENT.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src/self-annotate/src")
LIVE_IMPORT = os.path.join(ROOT, "src/pycsl")

# ABSENT is expected only for these SHAPES (constructors are inlined into the record's
# `by` witness; `__repr__` on a token record is modelled structurally).
EXPECTED_ABSENT = ("__init__", "__repr__")


def annotation_flags(lines, node):
    """(is_trusted, is_abstract) read off the `#@` block above a def.

    BLANK LINES may separate that block from the `def` (audit_proof_reverify.py puts two
    there), so blanks are skipped — stopping at the first non-comment line mis-classified
    12 trusted functions as un-trusted while this gate was being written.
    """
    i = min([d.lineno for d in node.decorator_list] + [node.lineno]) - 2
    trusted = abstract = False
    while i >= 0 and (lines[i].strip().startswith("#") or not lines[i].strip()):
        t = lines[i].strip()
        if t.startswith("#@ \\trusted"):
            trusted = True
        if t.startswith("#@ \\abstract"):
            abstract = True
        if not t and trusted:
            break
        i -= 1
    return trusted, abstract


def candidates(path):
    src = open(path).read()
    lines = src.split("\n")
    out = []

    def walk(node, cls):
        for c in ast.iter_child_nodes(node):
            if isinstance(c, ast.ClassDef):
                walk(c, cls + (c.name,))
            elif isinstance(c, (ast.FunctionDef, ast.AsyncFunctionDef)):
                trusted, abstract = annotation_flags(lines, c)
                if not trusted and not abstract:
                    out.append((cls, c.name))

    walk(ast.parse(src), ())
    return out


def emit(path):
    mlw = path[:-3] + ".mlw"
    if os.path.exists(mlw):
        os.remove(mlw)
    subprocess.run(
        [sys.executable, os.path.join(ROOT, "src/pycsl/pycsl.py"), path,
         "--import-path", LIVE_IMPORT, "--no-proof", "--keep-mlw"],
        capture_output=True, text=True, cwd=ROOT,
        env={**os.environ, "PYTHONHASHSEED": "0"}, timeout=1800)
    text = open(mlw).read() if os.path.exists(mlw) else ""
    if os.path.exists(mlw):
        os.remove(mlw)
    return text


def classify(name, text):
    b = re.escape(name)
    # `with <name>` is a mutual-recursion member of a `let rec … with …` group — a real
    # definition. Omitting it reported 10 false ABSENTs for the converted `_Parser` nest.
    if re.search(r"\b(let (rec |partial )?|with )"
                 r"(function |predicate |lemma |ghost )?[\w']*" + b + r"\b", text):
        return "LET"
    if re.search(r"\bval (function |predicate |ghost )?[\w']*" + b + r"\b", text):
        return "VAL"
    return "ABSENT"


def main():
    prefixes = sys.argv[1:]
    files = sorted(os.path.join(d, f)
                   for d, _, fs in os.walk(MIRROR) for f in fs if f.endswith(".py"))
    bad_val, bad_absent, total, lets = [], [], 0, 0
    for path in files:
        rel = os.path.relpath(path, MIRROR)
        if prefixes and not any(rel.startswith(p) for p in prefixes):
            continue
        cands = candidates(path)
        if not cands:
            continue
        text = emit(path)
        for cls, name in cands:
            total += 1
            status = classify(name, text)
            qn = ".".join(cls + (name,))
            if status == "LET":
                lets += 1
            elif status == "VAL":
                bad_val.append((rel, qn))
            elif name not in EXPECTED_ABSENT:
                bad_absent.append((rel, qn))

    for rel, qn in bad_val:
        print(f"[!] SILENTLY RE-ABSTRACTED: {rel}::{qn} — un-trusted but emitted as `val`. "
              f"Its marker is gone and nothing is verified in its place.")
    for rel, qn in bad_absent:
        print(f"[!] NOT EMITTED: {rel}::{qn} — un-trusted but absent from the emission "
              f"(and not a constructor/dunder).")
    print(f"[{'!' if bad_val or bad_absent else '+'}] untrusted-emitted: {total} un-trusted "
          f"function(s); {lets} emitted as definitions, {len(bad_val)} re-abstracted to "
          f"`val`, {len(bad_absent)} unexpectedly absent.")
    return 1 if (bad_val or bad_absent) else 0


if __name__ == "__main__":
    sys.exit(main())
