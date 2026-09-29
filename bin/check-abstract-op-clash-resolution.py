#!/usr/bin/env python3
r"""check-abstract-op-clash-resolution — `_add_abstract_op`'s same-arity tiebreak has teeth.

WHY IT EXISTS (#49, gen #33). `module6_whyml/abstract_ops.py::_add_abstract_op` deduplicates
abstract `val` declarations by name+arity. When two DIFFERENT declarations share a name and
an arity it used to resolve the clash with one line:

    # Same arity but different declaration -- keep longer
    if len(decl) > len(existing):

That is a HEURISTIC standing in for a semantic rule, and three core symbols are registered
in BOTH a polymorphic and an int-monomorphic spelling -- `map_update_some`,
`map_update_none`, `snapshot`. `_decl_arity` reads both spellings of each pair as the SAME
arity, so every one of them lands in that branch, and the int-monomorphic spelling is LONGER
in all three (`snapshot` by TWO characters, 35 vs 37). It also wins in BOTH registration
orders, because a stored decl is replaced only by a LONGER one. **So whenever both spellings
reached one emission the module collapsed to `int` -- which value model a shared symbol got
was decided by `len()`.** Reproduced from three lines (corpus 1916, and
`getting-better/open-routes/finding-the-int-erasure-seam-is-decided-by-string-length.md`):
an int-keyed set and a string-keyed set in ONE module emitted `map int (option int)` and
failed L3-tc with "This expression has type string, but is expected to have type int",
while EACH SET ALONE type-checked.

The tiebreak now has three branches, and this plane is the negative test for each:

  1. exactly one decl is POLYMORPHIC -> keep IT. It carries the same contract and
     instantiated at `int` IS the monomorphic decl, so it is strictly more general.
  2. neither subsumes the other and the heads differ in types or result -> REFUSE. There is
     no principled winner, so `len()` must not pick one.
  3. heads equivalent (binder grouping only) -> keep longer, unchanged, so the two clashes
     that actually occur in this tree (`str_eq_op`, `str_split_op`) stay byte-identical.

WHY A PLANE AND NOT A CORPUS WITNESS. Branch 2's population is EMPTY: no two registration
sites in the emitter currently produce a non-subsuming same-arity clash, so **no `.py` source
can make it fire** and no corpus witness can ever demonstrate it. That is the
NOT_SOURCE_REACHABLE shape, and `bin/check-refusal-witness-coverage.py` is explicit that such
an exclusion is "an exclusion with a GATE behind it, NOT an excuse" -- so this is that gate.
It drives the REAL `_add_abstract_op` (no reimplementation) and carries CONTROLS, so a
tiebreak that refused everything, or one that refused nothing, both fail.

Usage:  bin/check-abstract-op-clash-resolution.py [-v]
Exit 0 = all five legs hold.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src", "pycsl"))

POLY_SNAP = "val snapshot (a: array 'a) : seq 'a"
MONO_SNAP = "val snapshot (a: array int) : seq int"
POLY_MUS = ("val map_update_some (m: map 'k (option 'v)) (k: 'k) (v: 'v) "
            ": map 'k (option 'v)")
MONO_MUS = ("val map_update_some (m: map int (option int)) (k: int) (v: int) "
            ": map int (option int)")
# Cosmetic pair: binder GROUPING only. Both live in this tree today.
COSM_A = "val str_eq_op (a b: string) : bool"
COSM_B = "val str_eq_op (a: string) (b: string) : bool"
# Non-subsuming pair: same arity, DIFFERENT types, neither polymorphic.
CLASH_A = "val widget_op (a: string) : bool"
CLASH_B = "val widget_op (a: int) : bool"


def _fresh():
    """A bare carrier of the real mixin, with the one field `_add_abstract_op` touches."""
    from module6_whyml.abstract_ops import AbstractOpsMixin

    class _Carrier(AbstractOpsMixin):
        pass

    c = _Carrier()
    c._abstract_ops = {}
    return c


def _register(*decls):
    c = _fresh()
    for d in decls:
        c._add_abstract_op(d)
    return c._abstract_ops


def main() -> int:
    verbose = "-v" in sys.argv
    fails = []

    from errors import PyCSLSemanticError

    # LEG 0 — the pairs really do land in the same-arity branch. If `_decl_arity` ever
    # separates them, they take the `name_N` path instead and every leg below is vacuous.
    from module6_whyml.abstract_ops import AbstractOpsMixin as A
    for a, b, nm in ((POLY_SNAP, MONO_SNAP, "snapshot"),
                     (POLY_MUS, MONO_MUS, "map_update_some"),
                     (COSM_A, COSM_B, "str_eq_op"),
                     (CLASH_A, CLASH_B, "widget_op")):
        if A._decl_arity(a) != A._decl_arity(b):
            fails.append("LEG 0: %s's two spellings no longer have equal arity (%d vs %d), "
                         "so they take the name_N path and this plane measures NOTHING. "
                         "Re-derive the pairs." % (nm, A._decl_arity(a), A._decl_arity(b)))
    if verbose and not fails:
        print("[.] leg 0: all four pairs are same-arity, so they reach the tiebreak")

    # LEGS 1+2 — prefer the POLYMORPHIC decl, in BOTH registration orders. Order matters
    # because the old rule replaced a stored decl only by a LONGER one, so mono won either
    # way; a fix that only handled one order would pass a single-order test.
    for first, second, order in ((POLY_SNAP, MONO_SNAP, "poly-then-mono"),
                                 (MONO_SNAP, POLY_SNAP, "mono-then-poly")):
        got = _register(first, second).get("snapshot", "")
        if "'a" not in got:
            fails.append("LEG 1/2 (%s): the POLYMORPHIC `snapshot` did not survive; kept %r. "
                         "The int-monomorphic spelling is LONGER, so this is the seam "
                         "collapsing to `int` again." % (order, got))
        elif verbose:
            print("[.] leg 1/2 (%s): polymorphic `snapshot` kept" % order)
    for first, second, order in ((POLY_MUS, MONO_MUS, "poly-then-mono"),
                                 (MONO_MUS, POLY_MUS, "mono-then-poly")):
        got = _register(first, second).get("map_update_some", "")
        if "'k" not in got:
            fails.append("LEG 1/2 (%s): the POLYMORPHIC `map_update_some` did not survive; "
                         "kept %r." % (order, got))
        elif verbose:
            print("[.] leg 1/2 (%s): polymorphic `map_update_some` kept" % order)

    # LEG 3 — the REFUSAL fires on a non-subsuming same-arity clash. This is the leg that
    # discharges the witness debt: branch 2 is unreachable from any `.py` source.
    try:
        _register(CLASH_A, CLASH_B)
        fails.append("LEG 3: a non-subsuming same-arity clash (`%s` vs `%s`) was ACCEPTED. "
                     "The route-#64 refusal is gone, and string length decides a type again."
                     % (CLASH_A, CLASH_B))
    except PyCSLSemanticError as e:
        if "gen #33" not in str(e) and "neither of" not in str(e):
            fails.append("LEG 3: refused, but not by the clash guard: %s" % str(e)[:200])
        elif verbose:
            print("[.] leg 3: non-subsuming same-arity clash REFUSED")

    # LEG 4 — THE CONTROL. A guard that refused every clash would pass leg 3. The cosmetic
    # pair differs only in binder grouping and MUST still be accepted, keeping the longer
    # spelling exactly as before so the emission stays byte-identical.
    try:
        got = _register(COSM_A, COSM_B).get("str_eq_op", "")
        if got != COSM_B:
            fails.append("LEG 4: the cosmetic `str_eq_op` pair resolved to %r, not the "
                         "longer spelling %r — the byte-identical path changed." % (got, COSM_B))
        elif verbose:
            print("[.] leg 4: cosmetic pair accepted, longer spelling kept (byte-identical)")
    except PyCSLSemanticError as e:
        fails.append("LEG 4: the cosmetic pair (binder grouping only) was REFUSED — the "
                     "guard is over-firing and every emission that registers `str_eq_op` "
                     "twice would break: %s" % str(e)[:200])

    if fails:
        print("[-] abstract-op-clash-resolution: FAILED")
        for f in fails:
            print("    " + f)
        return 1
    print("[+] abstract-op-clash-resolution: OK — the polymorphic declaration wins in BOTH "
          "orders for `snapshot` and `map_update_some`, a non-subsuming same-arity clash is "
          "REFUSED, and the binder-grouping-only pair is still accepted with the longer "
          "spelling (byte-identical).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
