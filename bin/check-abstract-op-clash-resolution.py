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
  2. neither subsumes the other and the heads differ in types or result -> there is no
     principled winner. A runtime REFUSAL was written and then REMOVED: `_add_abstract_op`
     has a `\trusted` mirror stub in THREE mirror files, so one `raise` took
     `check-trusted-raises-honesty` SILENT 62 -> 65, and declaring `#@ raises` instead would
     cascade a `raises` clause into every mirror caller (lesson (c5) by the declared route).
     It bought nothing a GATE cannot: the clash is between declarations THE EMITTER ITSELF
     registers, so only an edit to `src/pycsl/` can create one. LEG 5 below is that gate.
  3. heads equivalent (binder grouping only) -> keep longer, unchanged, so the two clashes
     that actually occur in this tree (`str_eq_op`, `str_split_op`) stay byte-identical.

WHY A STATIC CENSUS RATHER THAN A RUNTIME REFUSAL. The non-subsuming clash cannot be reached
from any `.py` source -- it is a property of the emitter's OWN registration sites -- so the
honest place to catch it is where it would be INTRODUCED: a census of `src/pycsl/`. That also
keeps the raises ledger honest and owes no corpus witness. Legs 1-4 drive the REAL
`_add_abstract_op` (no reimplementation) with controls, so a tiebreak that preferred nothing
and one that preferred everything both fail; leg 5 is the census.

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

    # LEG 3 — a non-subsuming same-arity clash must NOT be silently resolved by length in a
    # way that loses information. With the refusal removed this is the documented
    # keep-longer fallback; what guards the hazard is LEG 5, which asserts no such clash
    # exists in the emitter at all. Here we only pin the BEHAVIOUR so it cannot drift
    # unnoticed: the longer decl wins, deterministically, in both orders.
    for first, second in ((CLASH_A, CLASH_B), (CLASH_B, CLASH_A)):
        got = _register(first, second).get("widget_op", "")
        if got != max(CLASH_A, CLASH_B, key=len):
            fails.append("LEG 3: a non-subsuming same-arity clash resolved to %r, which is "
                         "neither spelling's longer form — the fallback drifted." % got)
    if verbose and not fails:
        print("[.] leg 3: non-subsuming clash falls back to keep-longer, deterministically")

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
    except Exception as e:
        fails.append("LEG 4: the cosmetic pair (binder grouping only) RAISED — the tiebreak "
                     "is over-firing and every emission that registers `str_eq_op` twice "
                     "would break: %r: %s" % (type(e).__name__, str(e)[:200]))

    # LEG 5 — THE CENSUS, and it is the leg that guards the hazard. Every literal `val` /
    # `function` declaration in `src/pycsl/`, grouped by the symbol name the dedup computes.
    # A name carrying two same-arity declarations that differ in TYPES or RESULT, with
    # NEITHER polymorphic, has no principled winner and would be resolved by string length.
    # Today: none. The known clashes are `snapshot`/`map_update_some`/`map_update_none` (one
    # side polymorphic, leg 1/2's business) and `str_eq_op`/`str_split_op` (binder grouping
    # only, leg 4's business).
    import ast
    import collections
    import re as _re
    # THE FILTER IS THE INSTRUMENT. A loose version of this pattern manufactured SEVEN
    # false clashes on its first run, all of one family: `val constant <name>` made it
    # capture the KEYWORD `constant`; ordinary English prose ("function in the same block.")
    # matched `function <word>`; and `%`-formatted decls yielded the "name" `%s`. Read the
    # outlier rows. So: the keyword is consumed, the NAME may not itself be a Why3 keyword,
    # and the line must actually look like a declaration -- a ` : ` type ascription, a
    # parenthesised or empty binder list, and no placeholder anywhere.
    DECL = _re.compile(r"^\s*(?:val\s+function|val\s+constant|val|function|predicate|constant)"
                       r"\s+([A-Za-z_][A-Za-z_0-9']*)\s*(\(.*)?:\s*\S.*$")
    KEYWORDS = {"val", "function", "constant", "predicate", "type", "in", "let", "if",
                "then", "else", "with", "match", "use", "import", "clone", "axiom",
                "lemma", "goal", "ensures", "requires", "writes", "reads", "raises"}
    by_name = collections.defaultdict(set)
    for dirpath, _d, files in os.walk(os.path.join(ROOT, "src", "pycsl")):
        for fn in sorted(files):
            if not fn.endswith(".py"):
                continue
            try:
                tree = ast.parse(open(os.path.join(dirpath, fn), encoding="utf-8",
                                      errors="replace").read())
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    for line in node.value.splitlines():
                        if "%" in line or "{" in line or "<" in line:
                            continue          # a formatted/placeholder decl names nothing
                        m = DECL.match(line)
                        if m and m.group(1) not in KEYWORDS:
                            by_name[m.group(1)].add(line.strip())
    def _canon_head(h):
        tys = []
        for names, ty in _re.findall(r"\(([^():]*):([^()]*)\)", h):
            tys.extend([ty.strip()] * len(names.split()))
        res = h.rsplit(":", 1)[-1] if ":" in h else ""
        return _re.sub(r"\s+", "", "|".join(tys) + "->" + res)
    if len(by_name) < 40:
        fails.append("LEG 5: only %d declaration name(s) censused in src/pycsl/, expected far "
                     "more — the walk is broken, so \"no clash\" means nothing. REFUSAL, not a "
                     "pass." % len(by_name))
    else:
        bad = []
        for nm, decls in sorted(by_name.items()):
            if len(decls) < 2:
                continue
            for i, a in enumerate(sorted(decls)):
                for b in sorted(decls)[i + 1:]:
                    if A._decl_arity(a) != A._decl_arity(b):
                        continue                      # the name_N path
                    if "'" in a or "'" in b:
                        continue                      # one side polymorphic -> leg 1/2
                    if _canon_head(a) == _canon_head(b):
                        continue                      # binder grouping only -> leg 4
                    bad.append((nm, a, b))
        if bad:
            for nm, a, b in bad:
                fails.append("LEG 5: %s has two SAME-ARITY declarations that differ in types "
                             "or result, with NEITHER polymorphic, so the tiebreak would "
                             "resolve them by STRING LENGTH:\n        %s\n        %s"
                             % (nm, a, b))
        else:
            # NEGATIVE TEST for the detector itself: a "no clash" verdict from a predicate
            # that flags nothing looks exactly like a clean tree. Feed it the known-bad
            # synthetic pair and require it to fire.
            _a, _b = CLASH_A, CLASH_B
            _would_flag = (A._decl_arity(_a) == A._decl_arity(_b)
                           and "'" not in _a and "'" not in _b
                           and _canon_head(_a) != _canon_head(_b))
            if not _would_flag:
                fails.append("LEG 5 SELF-TEST: the clash predicate does NOT flag the known-bad "
                             "pair (%s | %s), so its \"no clash\" verdict means nothing."
                             % (_a, _b))
            elif verbose:
                print("[.] leg 5: %d declaration name(s) censused in src/pycsl/, no "
                      "non-subsuming same-arity clash; predicate self-test fires on the "
                      "known-bad pair" % len(by_name))

    if fails:
        print("[-] abstract-op-clash-resolution: FAILED")
        for f in fails:
            print("    " + f)
        return 1
    print("[+] abstract-op-clash-resolution: OK — the polymorphic declaration wins in BOTH "
          "orders for `snapshot` and `map_update_some`, the binder-grouping-only pair is "
          "still accepted with the longer spelling (byte-identical), and NO name in "
          "src/pycsl/ carries two same-arity declarations that differ in types or result "
          "with neither polymorphic.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
