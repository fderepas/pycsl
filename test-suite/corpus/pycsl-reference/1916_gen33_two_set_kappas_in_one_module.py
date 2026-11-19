r"""Test 1916 — gen #33 (expected PASS): TWO SET KAPPAS IN ONE MODULE.

CAPABILITY WITNESS for the `_add_abstract_op` prefer-general fix. Before it, this exact
program emitted `val map_update_some (m: map int (option int)) …` and FAILED L3-tc with
"This expression has type string, but is expected to have type int".

WHY IT FAILED, and it was not a missing feature. `statements.py` chooses the map-write
declaration PER SITE (`_poly = _mutable_state_classes or _set_kappa == "string"`), so the
int-keyed set below asked for the MONOMORPHIC spelling and the string-keyed set asked for
the POLYMORPHIC one. `_add_abstract_op` deduplicates by name+arity and both spellings have
the same arity, so it fell to the tiebreak — which was **"keep the LONGER string"**. The
int-monomorphic spelling is longer (for `snapshot`, by two characters), and it wins in BOTH
registration orders, so the module collapsed to `int` and the string use stopped
type-checking. `statements.py`'s own comment relies on "the name-dedup means ONE DECL SERVES
EVERY MAP WRITE IN THE MODULE"; which one it serves had never been decided.

EACH SET ALONE ALWAYS WORKED — an int-keyed set alone got MONO and type-checked, a
string-keyed set alone got POLY and type-checked. Only the COMBINATION broke, which is why
no per-feature test could catch it and why this witness pairs them deliberately.

The fix prefers the POLYMORPHIC declaration: it carries the same contract and instantiated
at `int` IS the monomorphic one, so it is strictly more general and never weaker.

Companion: `getting-better/open-routes/finding-the-int-erasure-seam-is-decided-by-string-length.md`.
Measured honestly there: the repair moves ZERO of the 37 recorded string<->int CONVERSION
blockers, so it is a real capability gain with no marker payoff — not a seam-wide fix.
"""


#@ ensures \result == 0
#@ assigns \nothing
def two_kappas() -> int:
    si = set()
    si.add(1)
    ss = set()
    ss.add("a")
    return 0
