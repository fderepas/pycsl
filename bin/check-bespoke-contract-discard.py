#!/usr/bin/env python3
r"""THE BESPOKE-LOWERING CONTRACT DISCARD — a declared `#@` clause that the emitter throws away.

WHY IT EXISTS (#49, gen #34). Module 6 has TWENTY-FIVE `*_bespoke` emitters in
`src/pycsl/module6_whyml/functions.py`: hand-written lowerings, each keyed on a mirror
METHOD NAME, that emit a faithful body for a construct the general path cannot model. Every
one of them writes its contract as two literal strings —

    functions.py:4445   "    requires { true }",
    functions.py:4446   "    ensures  { true }",

— and **not one of them reads `func`'s contract.** So a `#@ ensures` / `#@ assigns` /
`#@ raises` written on a bespoke-lowered mirror method is SILENTLY DISCARDED, and the mirror
source goes on reading as though it were proved.

MEASURED at the first look: 23 mirror methods reach a bespoke dispatch key, and **TWELVE
carry a non-trivial clause that never reaches the emission** — five
`#@ ensures \result["type"] == "<Kind>"` (the IR-construction FAITHFULNESS claims that layer
exists for), five `#@ assigns ir_stmts`, two `#@ assigns self._fresh_var_counter`, one
`#@ raises PyCSLSemanticError when True`.

HOW IT WAS FOUND, and the two wrong stories are part of the record. The emission of
`pycsltojsonemitter___py_expr_compare` carries `requires { true } ensures { true }` and
nothing else, while its same-group sibling `..._py_expr_unaryop` carries its
`ensures { (kind_of result) = "UnaryOp" }`, four frame-preservation `ensures` and `writes { }`.
Hypothesis 1 — "the droppers are the ones whose mirror return annotation is int-erased to
`-> int`" — is REFUTED: `_py_expr_unaryop` and `_py_expr_binop` are also `-> int` and keep
their clause. Hypothesis 2 — "the keepers are the ones carrying `#@ \diverges`" — is REFUTED
by measurement: adding `#@ \diverges` to `_py_expr_compare` in a disposable worktree and
re-emitting left the block unchanged AND dropped the `diverges` clause too, which is what
said the WHOLE contract block is bypassed. The real discriminator is simply: `unaryop` and
`binop` are NOT bespoke; `compare`, `boolop` and the four comprehensions are.

>>> **"FAITHFUL" SAID OF A LOWERING IS A CLAIM ABOUT THE BODY UNLESS THE SENTENCE SAYS
>>> OTHERWISE, AND THE CONTRACT IS THE HALF NOBODY RE-READS.** The mirror's own comment beside
>>> `_py_expr_compare` says the bespoke lowering "emits it FAITHFULLY as the certified `IrBinOp`
>>> ctor" — true of the body, silent about the contract.

WHAT THIS GATE CHECKS, and why it is the right shape. Every discarded clause is WEAKER than
declared (an `ensures { true }` proves less; a missing `writes` on a concrete `let` lets Why3
infer the real effect instead of believing an empty one), so the class is FAIL-CLOSED — nothing
false is derived. The hazard is therefore not unsoundness but a claim the artifact does not
prove, which is exactly the hazard `bin/check-emit-ir-arm-postconditions.py` was built for one
step away: that plane exists because an emit_ir arm was *"sound only while the methods that
REACH them carry no real postcondition, and until now that was PROSE."* Same argument, same
missing gate, a different emitter. So:

    RATCHET: the number of bespoke-reached mirror methods carrying a non-trivial clause may
             only SHRINK. It falls when a bespoke emitter learns to emit the real contract
             (the REAL fix, scoped in
             getting-better/open-routes/finding-gen34-five-mirror-contracts-emit-nothing.md)
             or when a clause that was never going to be emitted is removed from the source.

A NOTE ON `#@ \diverges`, deliberately EXCLUDED from the count: it is a PERMISSION, not a
claim. Dropping it makes the emitted declaration owe a termination argument, i.e. STRICTER, so
its loss cannot hide a falsehood. It is reported separately and not ratcheted.

STALENESS REFUSAL (the #44 rule: a gate that cannot tell "nothing is wrong" from "I looked at
nothing" is not a gate). The dispatch keys below are literals from `functions.py`. If a key no
longer occurs there it has been renamed and this gate is silently measuring a smaller
population, so the gate REFUSES (exit 2) rather than printing a smaller number.

EXIT CODES
  0  offenders <= MAX_DISCARDED
  1  offenders above the ratchet
  2  refusal: a dispatch key went stale, or the bespoke emitters stopped hard-coding, or the
     reached population collapsed
"""
from __future__ import annotations

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")
EMITTER = os.path.join(ROOT, "src", "pycsl", "module6_whyml", "functions.py")

# The method-name SUFFIXES each bespoke lowering keys on, read off the dispatch site in
# functions.py (`nm.endswith("...")` / `name == src` for the recognizer trio).
BESPOKE_KEYS = [
    "_py_stmt_try", "_py_stmt_match", "_py_stmt_delete", "_py_stmt_assign",
    "_py_stmt_with", "_py_expr_lambda", "_py_expr_dict", "_py_expr_listcomp",
    "_py_expr_genexp", "_py_expr_setcomp", "_py_expr_dictcomp", "_py_expr_compare",
    "_py_expr_boolop", "_emit_ghost_assign",
    "_is_typeddict_class", "_is_namedtuple_class", "_is_protocol_class",
    "_should_skip_method", "_build_overload_param_guard", "_synthesize_overload_guard",
    "_is_overload_stub", "_act_guard", "_is_final_annotation",
]

# RATCHET. (#49) gen #34 first measurement: 12 methods.
MAX_DISCARDED = 12
# Floors. 23 methods reached at the first measurement; 25 bespoke emitters.
MIN_REACHED = 18
MIN_BESPOKE_EMITTERS = 20

TRIVIAL = (
    re.compile(r"^#@\s*requires\s+True$"),
    re.compile(r"^#@\s*ensures\s+True$"),
    re.compile(r"^#@\s*assigns\s+\\nothing$"),
    re.compile(r"^#@\s*\\trusted\b"),
    re.compile(r"^#@\s*\\abstract\b"),
    re.compile(r"^#@\s*sibling_concrete\b"),
    re.compile(r"^#@\s*no_inline\b"),
)
# A PERMISSION, not a claim: losing it makes the declaration stricter. Reported, not counted.
PERMISSION = re.compile(r"^#@\s*\\diverges$")


def _clauses_above(lines, i):
    """The `#@` block attached to the `def` at line index i, nearest-first."""
    out = []
    for k in range(i - 1, max(i - 30, -1), -1):
        s = lines[k].strip()
        if s.startswith("#@"):
            out.append(s)
        elif s.startswith("#") or s.startswith("@") or s == "":
            continue
        else:
            break
    return out


def measure(extra_clause=None):
    """-> (reached, offenders, permissions) over the mirror.

    `extra_clause` injects one synthetic non-trivial clause onto the FIRST reached method
    that currently has none, for the negative test.
    """
    reached, offenders, perms = [], [], []
    injected = False
    for dirpath, dirnames, files in os.walk(MIRROR):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for f in sorted(files):
            if not f.endswith(".py"):
                continue
            p = os.path.join(dirpath, f)
            rel = os.path.relpath(p, MIRROR)
            lines = open(p, encoding="utf-8").read().split("\n")
            for i, ln in enumerate(lines):
                m = re.match(r"\s*def (\w+)\(", ln)
                if not m:
                    continue
                nm = m.group(1)
                if not any(nm.endswith(k) for k in BESPOKE_KEYS):
                    continue
                cl = _clauses_above(lines, i)
                real = [c for c in cl
                        if not any(t.match(c) for t in TRIVIAL) and not PERMISSION.match(c)]
                if PERMISSION.search("\n".join(cl)):
                    perms.append((rel, nm))
                reached.append((rel, nm))
                if extra_clause is not None and not real and not injected:
                    real = [extra_clause]
                    injected = True
                if real:
                    offenders.append((rel, nm, real))
    return reached, offenders, perms


def _emitter_facts():
    """(n_bespoke_emitters, n_hardcoding, stale_keys)."""
    src = open(EMITTER, encoding="utf-8").read()
    lines = src.split("\n")
    idx = [(i, mm.group(1)) for i, l in enumerate(lines)
           for mm in [re.match(r"    def (\w*bespoke\w*)\(", l)] if mm]
    hard = 0
    for j, (i, _n) in enumerate(idx):
        end = idx[j + 1][0] if j + 1 < len(idx) else len(lines)
        blk = "\n".join(lines[i:end])
        if "requires { true }" in blk or "_expr_bespoke_body(" in blk:
            hard += 1
    stale = [k for k in BESPOKE_KEYS if ('"%s"' % k) not in src]
    return len(idx), hard, stale


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--self-test", action="store_true",
                    help="inject a real `#@ ensures` onto a currently-clean bespoke method "
                         "and require the count to RISE")
    args = ap.parse_args()

    n_bespoke, n_hard, stale = _emitter_facts()
    if stale:
        print("[!] bespoke-contract-discard: %d dispatch key(s) no longer occur in "
              "functions.py — %s. A renamed key means this gate is measuring a SMALLER "
              "population than it thinks. REFUSING." % (len(stale), ", ".join(stale)),
              file=sys.stderr)
        return 2
    if n_bespoke < MIN_BESPOKE_EMITTERS:
        print("[!] bespoke-contract-discard: only %d `*_bespoke` emitter(s) found in "
              "functions.py, below the floor of %d. The walk is broken. REFUSING."
              % (n_bespoke, MIN_BESPOKE_EMITTERS), file=sys.stderr)
        return 2

    reached, offenders, perms = measure()
    if len(reached) < MIN_REACHED:
        print("[!] bespoke-contract-discard: only %d mirror method(s) reach a bespoke "
              "dispatch key, below the floor of %d. REFUSING."
              % (len(reached), MIN_REACHED), file=sys.stderr)
        return 2

    if args.self_test:
        _r, off2, _p = measure(extra_clause='#@ ensures \\result == 42')
        if len(off2) <= len(offenders):
            print("[!] bespoke-contract-discard --self-test: FAILED — injecting a real "
                  "`#@ ensures` onto a clean bespoke-reached method did NOT raise the count "
                  "(%d -> %d), so the detector is INERT and its number means nothing."
                  % (len(offenders), len(off2)), file=sys.stderr)
            return 1
        print("[+] bespoke-contract-discard --self-test: OK — injecting one real "
              "`#@ ensures` takes the count %d -> %d. The detector has teeth."
              % (len(offenders), len(off2)))
        return 0

    if args.list:
        for rel, nm, real in sorted(offenders):
            print("    %-34s %-30s %s" % (rel, nm, "; ".join(c[:90] for c in real)))

    print("[*] bespoke-contract-discard: %d `*_bespoke` emitter(s) in functions.py, %d of "
          "which hard-code their contract; %d mirror method(s) reach a bespoke dispatch key; "
          "%d carry a NON-TRIVIAL clause the lowering discards (%d carry `\\diverges`, a "
          "permission whose loss is stricter and is not counted)."
          % (n_bespoke, n_hard, len(reached), len(offenders), len(perms)))

    if len(offenders) > MAX_DISCARDED:
        print("[!] bespoke-contract-discard: %d > ratchet %d. A mirror method reached by a "
              "bespoke lowering gained a clause that the lowering THROWS AWAY, so the source "
              "reads as a guarantee and the emission claims nothing. Either teach that "
              "bespoke emitter to emit the declared contract, or do not declare it."
              % (len(offenders), MAX_DISCARDED), file=sys.stderr)
        for rel, nm, real in sorted(offenders):
            print("      %-34s %-30s %s" % (rel, nm, "; ".join(c[:90] for c in real)),
                  file=sys.stderr)
        return 1
    print("[+] bespoke-contract-discard: OK — %d discarded-clause method(s) (ratchet %d, may "
          "only shrink)." % (len(offenders), MAX_DISCARDED))
    return 0


if __name__ == "__main__":
    sys.exit(main())
