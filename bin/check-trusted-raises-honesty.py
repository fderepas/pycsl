#!/usr/bin/env python3
r"""check-trusted-raises-honesty.py — the TRUSTED-RAISES plane.

A `#@ \trusted` mirror stub is believed, not proved: its `#@ requires` / `#@ ensures` /
`#@ assigns` / `#@ raises` are asserted by a reviewer and Module 6 emits a bodyless `val`
carrying exactly them. `check-trusted-frame-honesty.py` already asks whether such a stub's
`#@ assigns` is honest about what the LIVE body WRITES. Nobody had asked the sibling
question:

    IS THE STUB HONEST ABOUT WHAT THE LIVE BODY *RAISES*?

It matters for the same reason the frame does. An emitted `val` with NO `raises` clause
tells Why3 the call CANNOT raise. Every caller then reasons on a single exit path: a
`try/except` around the call has a handler Why3 knows is dead, and the caller's own
contract need not account for the exceptional exit. If the live body does contain a
`raise`, the stub is asserting something false — and unlike a missing `assigns`, nothing
in the proof will ever contradict it, because a `\trusted` body is never lowered.

This is the shape of routes #20 and #21 one level up: a claim that a control-flow path
does not exist, believed because nothing looks.

*** PROBED, AND IT IS A TRUST SURFACE RATHER THAN A DEMONSTRATED UNSOUNDNESS. *** The
obvious exploit — a `\trusted` stub whose body is `raise ValueError(...)`, called inside a
`try/except ValueError` whose handler returns a different value, with a contract asserting
the non-exceptional result — was built and run (`scratchpad/w9/probes/tr1.py`) and
correctly FAILS. The reason is the honest one: whatever such a stub's contract claims is
claimed BY THE REVIEWER, and `\trusted` means exactly that. A stub that says
`ensures \result == 1` over a body that always raises is a FALSE REVIEW, not a broken
lowering.

That is why this is a RATCHET and not a route. What it measures is how much of the mirror's
believed surface makes a control-flow claim nobody checked, and the honest thing to do with
such a number is to publish it and shrink it.

WHAT IT MEASURES. For every `\trusted` mirror stub, whether its LIVE counterpart contains
a `raise` statement, and whether the stub carries a `#@ raises` line.

    DECLARED   live body raises, stub says so.
    SILENT     live body raises, stub says NOTHING.  <- the population held by the ratchet
    (a stub whose live body has no `raise` is not counted either way)

It is a LOWER BOUND in one direction and an over-count in the other, and both are stated
rather than hidden: only DIRECT `raise` statements are counted, so a stub whose live body
raises only through a callee is missed; and a `raise` on a path the contract's `#@
requires` excludes is counted although the stub may be honest. The ratchet is therefore a
measurement to shrink, not a bug count.

FIRST MEASUREMENT (#44): 70 `\trusted` stubs have a raising live counterpart; 2 declare
`#@ raises` and 68 are SILENT.

USAGE
    bin/check-trusted-raises-honesty.py [--verbose] [--max-silent N]
"""
import argparse
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")
LIVE = os.path.join(ROOT, "src", "pycsl")

# RATCHET HISTORY, itemised so a bump is never a shrug:
#   68  first measurement (#44).
#   70  (#49) TWO REFUSALS were added by the campaign itself and BOTH are deliberate
#       fail-closed devices, each landed with witnesses that prove a contract FALSE of its
#       program at the parent commit:
#         `_handle_augassign_stmt`  route #49 — `a += [1]` on a list PARAMETER was dropped
#         `_handle_binop`           route #46 — a comparison over a possibly-NaN name
#       Both raise `PyCSLSemanticError`, i.e. they REJECT THE FILE; neither adds an exit
#       path to a lowering. The rows are tagged `SILENT/refusal` so this stays visible.
#       NOT bumped for anything else: the non-refusal population is unchanged at 68.
#   69  (#49, convergence-metric Phase 4) LOWERED BY DECLARING, never by moving the bound.
#       `frontend/exec_splice.py::_ExecSplicer.visit_Expr` now carries
#       `#@ raises PyCSLParseError when True`. Whole-file re-proof rc=0, zero non-Valid
#       goals (`getting-better/proofs49/cm4_exec_splice.rc` + `.log`, 2m14s).
#       *** THE `when True` IS AN OVER-APPROXIMATION AND IS DECLARED AS ONE. *** The live
#       body raises `PyCSLParseError` on exactly three paths, all of them reachable only
#       when `_is_constant_exec(val)` holds: the `exec(...)` literal fails to parse, a
#       spliced statement is outside `_WHITELIST`, or the splice contains a nested `exec`.
#       That condition is not expressible against the stub's parameter, which lowers to an
#       opaque `int`, so the honest move is the over-approximation plus this note — the
#       same shape as `ir_schema.py:171` and `desugar.py:56`, which also say `when True`.
#       An over-approximating `raises` is still STRICTLY WEAKER (hence safer) than the
#       silent stub it replaces: no-clause told Why3 the call CANNOT raise.
#   62  (#49, convergence-metric Phase 4, SECOND batch) LOWERED BY DECLARING, 69 -> 62.
#       SEVEN stubs in SIX mirror files, chosen for the cheap property gen #16 measured —
#       a `raises` on a val DECLARED BUT NEVER APPLIED IN-FILE adds no VC. That property
#       was VERIFIED PER STUB BEFORE EDITING against the baseline `.mlw`: each of the seven
#       occurs exactly once in its emission, at its own `val` line, and nowhere else (the
#       only other hits are derived union TYPE names such as `_union__inline_calls_2`,
#       which are declarations, not applications).
#         proof2why3/crosscheck.py::_load_axiom_registry        raises RuntimeError
#         proof2why3/crosscheck_ir.py::_load_axiom_registry     raises RuntimeError
#         proof2why3/sertop.py::_sexp_parse                     raises ValueError
#         frontend/ConcurrencyChecker.py::check                 raises PyCSLSemanticError
#         frontend/import_classifier.py::check_imports          raises PyCSLSemanticError
#         frontend/ir_inline.py::_expand                        raises PyCSLSemanticError
#         frontend/ir_inline.py::_inline_calls                  raises PyCSLSemanticError
#       Each exception name is the one the LIVE body actually raises, read off the live AST
#       (this file's `declared` test only looks for the WORD `raises`, so the name is on the
#       author, not on the tool — it was checked by hand per stub).
#       *** ALL SEVEN `when True` ARE OVER-APPROXIMATIONS AND ARE DECLARED AS ONES. ***
#       The real conditions, none expressible against the stub signatures:
#         `_load_axiom_registry` takes NO parameters and raises iff `_AXIOM_REGISTRY` is
#           absent from `module6_whyml/preamble.py` — a property of a file read at run time,
#           not of any argument;
#         `_sexp_parse` raises on empty input, an unterminated list, or a stray `)`. The
#           FIRST path alone would be expressible (`tokens` lowers to `array string`), but
#           declaring only it would UNDER-approximate, which is a FALSE declaration; the
#           other two are content- and recursion-dependent;
#         `check` raises iff `self.strict_mode` AND `self.warnings` is non-empty — but
#           `warnings` is populated DURING the call, so no entry state determines it;
#         `check_imports`, `_expand`, `_inline_calls` depend on AST/IR content behind an
#           opaque `int`.
#       Same shape as `ir_schema.py:171`, `desugar.py:56`, `exec_splice.py:38`.
#       An over-approximating `raises` is still STRICTLY WEAKER (hence safer) than the
#       silent stub it replaces: no-clause told Why3 the call CANNOT raise.
#       Acceptance: emit + `why3 prove --type-only` rc=0 on all 6 files, and every file
#       GREW (so this is NOT the refused-file false green that Phase 3's `reason:` token
#       produced); emission diff is EXACTLY 7 `raises { E -> true }` clauses + 4 new
#       `exception` declarations and nothing else; whole-file re-proofs rc=0 with zero
#       non-Valid goals counted INDEPENDENTLY of the SUCCESS banner
#       (`getting-better/proofs49/cm5_*.{log,rc}`); markers unchanged at 459.
MAX_SILENT = 62


# (#49) THE REFUSAL CLASS. Every `raise` this campaign ADDS to the emitter is a REFUSAL —
# a `PyCSL*Error` that ABORTS the whole pipeline and rejects the file — and a refusal is
# not an exit path of the modelled computation: no caller observes it, because there is no
# run. That is a different thing from a `raise` the emitter uses as control flow, and the
# ratchet was measuring them as one. Both are still counted (nothing is hidden and the
# SILENT number does not move), but each row now says which it is, so the next reader can
# tell a growing refusal surface — which is the campaign WORKING — from a growing
# unchecked-control-flow surface, which is the thing this plane exists to shrink.
_REFUSAL_PREFIXES = ("PyCSL", "_PyCSL")


def _alias_map(tree):
    """{local alias: original name} for `from errors import PyCSLSemanticError as _R49`.
    The campaign's refusals are spelled with such aliases — measured: route #49's
    `_handle_augassign_stmt` raises `_R49`/`_R49B` and was tagged as ordinary control flow
    until this map existed."""
    out = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            for a in n.names:
                if a.asname:
                    out[a.asname] = a.name
    return out


def _raise_kinds(fn_node, aliases=None):
    """The set of exception NAMES raised directly in this function (`<bare>` for a
    bare `raise`)."""
    ks = set()
    for x in ast.walk(fn_node):
        if not isinstance(x, ast.Raise):
            continue
        e = x.exc
        nm = None
        if isinstance(e, ast.Call) and isinstance(e.func, ast.Name):
            nm = e.func.id
        elif isinstance(e, ast.Call) and isinstance(e.func, ast.Attribute):
            nm = e.func.attr
        elif isinstance(e, ast.Name):
            nm = e.id
        nm = nm or "<bare>"
        ks.add((aliases or {}).get(nm, nm))
    return ks


def raising_live_functions():
    """{name: set(files)} for every LIVE function containing a direct `raise`."""
    out = {}
    for root, _d, files in os.walk(LIVE):
        for fn in sorted(files):
            if not fn.endswith(".py"):
                continue
            path = os.path.join(root, fn)
            try:
                tree = ast.parse(open(path, errors="replace").read())
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue
            for n in ast.walk(tree):
                if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if any(isinstance(x, ast.Raise) for x in ast.walk(n)):
                    out.setdefault(n.name, set()).add(os.path.relpath(path, ROOT))
                    KINDS.setdefault(n.name, set()).update(
                        _raise_kinds(n, _alias_map(tree)))
    return out


KINDS = {}


def directive_block(lines, lineno):
    """The contiguous comment block immediately above a def."""
    blk = []
    for line in reversed(lines[max(0, lineno - 45):lineno - 1]):
        if line.strip().startswith("#") or not line.strip():
            blk.append(line)
        else:
            break
    return blk


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--max-silent", type=int, default=MAX_SILENT)
    args = ap.parse_args()

    raising = raising_live_functions()
    declared, silent = [], []
    for root, _d, files in os.walk(MIRROR):
        for fn in sorted(files):
            if not fn.endswith(".py"):
                continue
            path = os.path.join(root, fn)
            try:
                src = open(path, errors="replace").read()
                tree = ast.parse(src)
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue
            lines = src.split("\n")
            for n in ast.walk(tree):
                if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                blk = directive_block(lines, n.lineno)
                # THE DIRECTIVE, NOT A PROSE MENTION (gen #4). The polarity here is the
                # SAFE one — a prose mention ADDS a converted method to the audited
                # `\\trusted` population rather than hiding one — but it still
                # mis-reports which stubs are assumed and can move the MAX_SILENT
                # ratchet for a reason that is not about trust at all.
                if not any(b.strip().startswith("#@") and "\\trusted" in b for b in blk):
                    continue
                if n.name not in raising:
                    continue
                rel = os.path.relpath(path, MIRROR)
                row = (rel, n.name, sorted(raising[n.name])[0])
                # ANCHORED TOO (gen #4). The `\trusted` test three lines up was hardened to
                # require the `#@` prefix; this one was left behind in the same pass, and it
                # is the same hazard one directive over — a justification comment that NAMES
                # `#@ raises` in prose moves a genuinely SILENT stub into `declared`, which
                # SHRINKS the population the MAX_SILENT ratchet is guarding.
                if any(b.strip().startswith("#@") and "raises" in b for b in blk):
                    declared.append(row)
                else:
                    silent.append(row)

    total = len(declared) + len(silent)
    print(f"[*] trusted-raises-honesty: {total} `\\trusted` stub(s) whose LIVE counterpart "
          f"contains a `raise`; {len(declared)} declare `#@ raises`, {len(silent)} are "
          f"SILENT (the emitted `val` tells Why3 the call CANNOT raise).")
    if args.verbose or len(silent) > args.max_silent:
        for rel, name, livefile in sorted(silent):
            _k = KINDS.get(name, set())
            _tag = ("SILENT/refusal" if _k and all(
                any(x.startswith(pfx) for pfx in _REFUSAL_PREFIXES) for x in _k)
                else "SILENT")
            print(f"    {_tag:15s} {rel:44s} {name:38s} live: {livefile}")
    if len(silent) > args.max_silent:
        print(f"[-] trusted-raises-honesty: SILENT RATCHET BROKEN — {len(silent)} > "
              f"{args.max_silent}. A `\\trusted` stub with no `#@ raises` asserts that its "
              f"call has ONE exit path; nothing will ever contradict it, because a "
              f"`\\trusted` body is never lowered.")
        return 1
    if len(silent) < args.max_silent:
        print(f"[+] trusted-raises-honesty: silent {len(silent)} < ratchet "
              f"{args.max_silent} — lower the constant.")
    print(f"[+] trusted-raises-honesty: OK — measured {len(declared)} declared / "
          f"{len(silent)} silent (ratchet {args.max_silent}). NOTE: direct `raise` "
          f"statements only, so this is a LOWER BOUND on the population.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
