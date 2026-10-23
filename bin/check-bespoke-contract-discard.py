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

KNOWN POPULATION GAP — THIS GATE IS NOT COMPLETE AND MUST NOT READ AS THOUGH IT WERE.
(#49) gen #34, from a delegated census run the same day: `*_bespoke` in `functions.py` was NOT the
whole hard-coded-contract population.
  * `src/pycsl/module6_whyml/generic_fold.py` has ~48 `emit_*_group` templaters which emit the
    MIRROR METHOD'S OWN symbol with a literal `requires { true } ensures { true }` and never read
    `func["contracts"]`. 195 mirror-method symbols carry that one-line spelling in the emission. Of
    the twelve whose source method has a non-trivial clause, exactly ONE is a genuine discard:
    `generic_fold.py:7592` (`emit_dictfold_group`) drops
    `#@ assigns self._tuple_var_slot_types` from `TypeInferenceMixin._collect_tuple_var_assigns`,
    emitted receiver-less and frame-less at `Module6_WhyMLTranspiler.mlw:3391`.
  * `functions.py:8041` (`_emit_term_pp_delegation`) hard-codes too. It fires today only on `pp`
    methods that claim nothing, so it is LATENT: one non-trivial `#@ ensures` on a delegated `pp`
    and it becomes the defect.
Neither is in `BESPOKE_KEYS`, so neither is counted here. **The right generalisation is to stop
keying on the EMITTER and measure from the EMISSION instead** — every emitted declaration whose
contract block is exactly the hard-coded fingerprint while its SOURCE method declares something —
which is key-independent and covers emitter paths nobody has written yet. That needs its own
measurement and its own negative test (and must exclude IMPORT stubs, where backlog #60a drops
`\result["key"]` clauses DELIBERATELY and soundly), so it is recorded as the follow-up rather than
bolted on. Backlog #74.

EXIT CODES
  0  population <= MAX_DECLARED, and (with --emit-dir) discarded <= MAX_DISCARDED
  1  either count above its ratchet
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

# TWO RATCHETS, because a SOURCE count and an EMISSION count are different measurements and
# conflating them is how this gate would have lied in both directions.
#   MAX_DECLARED  — bespoke-reached mirror methods carrying a non-trivial clause. A ceiling on
#                   the POPULATION AT RISK. Measured 12.
#   MAX_DISCARDED — of those, the ones whose clause is provably ABSENT from the emitted
#                   declaration (`--emit-dir`). **Measured SEVEN, not twelve** — the five
#                   `#@ assigns ir_stmts` stmt-handlers DO get a `writes` clause, so the
#                   source-only count OVERSTATED the defect by five. This is the real ratchet
#                   and it may only SHRINK. Without `--emit-dir` the gate can only check the
#                   population ceiling and says so.
MAX_DECLARED = 12
#   (#49) gen #34 — 7 -> 2 IN THE SAME GENERATION THAT MEASURED THE 7. `_expr_bespoke_body`
#   and `_emit_py_expr_compare_bespoke` now lower the DECLARED `requires`/`ensures` instead of
#   hard-coding them, so the five `#@ ensures \result["type"] == "<Kind>"` IR-faithfulness
#   postconditions EMIT and DISCHARGE (145 000 solver steps each; the goal TOTAL did not move
#   because each previously carried `ensures { true }` — a count that does not move is not
#   evidence that nothing changed). The RESIDUE IS TWO, both `#@ assigns self._fresh_var_counter`
#   (`_emit_ghost_assign`, `_synthesize_overload_guard`), and they are deliberately separate:
#   emitting a `writes` clause on a CONCRETE `let` CHECKS the frame against the body, so unlike
#   the `ensures` half it can FAIL. Backlog #74.
MAX_DISCARDED = 2
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



# ---------------------------------------------------------------------------------
# THE EMISSION ARM. Counting a SOURCE clause is not the measurement — the measurement is
# "declared and NOT EMITTED". A source-only count cannot tell a discarded clause from one a
# repaired scaffold now emits, so it would read as RED forever after the fix and could never
# ratchet down. Mapping, one line per clause kind, stated so it can be argued with:
#
#     #@ requires X   ->  a `requires { ... }` line that is not `{ true }`
#     #@ ensures  X   ->  an `ensures  { ... }` line that is not `{ true }`
#     #@ assigns  t   ->  a `writes { ... }` clause
#     #@ raises E ..  ->  a `raises { ... }` clause
#
# A method with no emitted declaration at all is INDETERMINATE and is reported, never counted
# as either satisfied or discarded — `bin/check-mirror-coverage.py` owns that population.

CLAUSE_KIND = (
    (re.compile(r"^#@\s*requires\s+"), "requires"),
    (re.compile(r"^#@\s*ensures\s+"), "ensures"),
    (re.compile(r"^#@\s*assigns\s+"), "assigns"),
    (re.compile(r"^#@\s*raises\s+"), "raises"),
)


def _class_of(path, defname):
    """The class a mirror `def` belongs to, by walking back to the nearest `class`."""
    lines = open(path, encoding="utf-8").read().split("\n")
    for i, l in enumerate(lines):
        if re.match(r"\s*def %s\(" % re.escape(defname), l):
            for k in range(i, -1, -1):
                mc = re.match(r"class (\w+)", lines[k])
                if mc:
                    return mc.group(1)
    return None


def _emitted_decls(emit_dir):
    """{symbol: contract-block text} over every .mlw in emit_dir."""
    out = {}
    for f in sorted(os.listdir(emit_dir)):
        if not f.endswith(".mlw"):
            continue
        lines = open(os.path.join(emit_dir, f), encoding="utf-8").read().split("\n")
        starts = [(i, mm.group(1)) for i, l in enumerate(lines)
                  for mm in [re.match(r"\s*(?:let|val|with)\s+(?:rec\s+|ghost\s+|function\s+)*(\w+)\s*\(", l)]
                  if mm]
        for j, (i, nm) in enumerate(starts):
            end = starts[j + 1][0] if j + 1 < len(starts) else len(lines)
            blk = []
            for l in lines[i + 1:end]:
                if l.strip() == "=" or l.strip().startswith("= "):
                    break
                blk.append(l)
            out.setdefault(nm, []).append("\n".join(blk))
    return out


def _sym(cls, defname):
    return "%s___%s" % (cls.lower(), defname.lstrip("_"))


def _kind_present(kind, blk):
    if kind == "requires":
        return any(re.match(r"\s*requires\s*\{", l) and l.strip() != "requires { true }"
                   for l in blk.split("\n"))
    if kind == "ensures":
        return any(re.match(r"\s*ensures\s*\{", l) and "{ true }" not in l
                   for l in blk.split("\n"))
    if kind == "assigns":
        return "writes {" in blk
    if kind == "raises":
        return "raises {" in blk
    return True


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
    ap.add_argument("--emit-dir",
                    help="a mirror emission (bin/mirror-emit-sweep.sh). With it the gate\n                         measures DECLARED-AND-NOT-EMITTED per clause kind, which is the\n                         real question; without it only the source population is reported.")
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

    if args.emit_dir:
        if not os.path.isdir(args.emit_dir):
            print("[!] bespoke-contract-discard: --emit-dir %s is not a directory."
                  % args.emit_dir, file=sys.stderr)
            return 2
        decls = _emitted_decls(args.emit_dir)
        discarded, indet = [], []
        for rel, nm, real in offenders:
            cls = _class_of(os.path.join(MIRROR, rel), nm)
            sym = _sym(cls, nm) if cls else None
            blks = decls.get(sym) if sym else None
            if not blks:
                indet.append((rel, nm, sym))
                continue
            lost = []
            for c in real:
                kind = next((k for rx, k in CLAUSE_KIND if rx.match(c)), None)
                if kind is None:
                    continue
                if not any(_kind_present(kind, b) for b in blks):
                    lost.append(c)
            if lost:
                discarded.append((rel, nm, lost))
        print("[*] bespoke-contract-discard --emit-dir: %d method(s) with a non-trivial "
              "clause; %d have it DISCARDED from the emission, %d have no emitted "
              "declaration at all (INDETERMINATE, not counted — check-mirror-coverage owns "
              "that population)." % (len(offenders), len(discarded), len(indet)))
        for rel, nm, lost in sorted(discarded):
            print("      %-34s %-30s %s" % (rel, nm, "; ".join(c[:90] for c in lost)))
        if len(discarded) > MAX_DISCARDED:
            print("[!] bespoke-contract-discard: %d DISCARDED > ratchet %d."
                  % (len(discarded), MAX_DISCARDED), file=sys.stderr)
            return 1
        print("[+] bespoke-contract-discard: OK — %d discarded (ratchet %d, may only shrink)."
              % (len(discarded), MAX_DISCARDED))
        return 0

    if len(offenders) > MAX_DECLARED:
        print("[!] bespoke-contract-discard: %d > population ceiling %d. A mirror method reached by a "
              "bespoke lowering gained a clause that the lowering THROWS AWAY, so the source "
              "reads as a guarantee and the emission claims nothing. Either teach that "
              "bespoke emitter to emit the declared contract, or do not declare it."
              % (len(offenders), MAX_DECLARED), file=sys.stderr)
        for rel, nm, real in sorted(offenders):
            print("      %-34s %-30s %s" % (rel, nm, "; ".join(c[:90] for c in real)),
                  file=sys.stderr)
        return 1
    print("[+] bespoke-contract-discard: OK — %d method(s) at risk (population ceiling %d). "
          "NO VERDICT ON DISCARD without --emit-dir; the `--slow` battery supplies it."
          % (len(offenders), MAX_DECLARED))
    return 0


if __name__ == "__main__":
    sys.exit(main())
