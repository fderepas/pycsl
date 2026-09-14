# ROUTE #114 — a TUPLE in an int position (a dict key) is replaced by a HASH OF ITS LOWERED
# TEXT, so `(y, 1)` is the SAME key before and after `y` changes

**Status: FOUND, REPRODUCED, BOTH DIRECTIONS MEASURED (gen #23, 2026-09-14). NOT REPAIRED.**
**Severity: SEV-1. First-order.** `d[(y, 1)]` is ordinary Python; no adversarial naming.

## PROVENANCE

Generator `substring-census`, same arm as route #113, probed as its sibling. The arm's own
docstring calls tuple->hash a "benign documented collapse (A7)". **A collapse that hashes the
TEXT of a term containing a mutable variable is not benign: text is not value.**

## THE MECHANISM, quoted

`src/pycsl/module6_whyml/expressions.py`, `_coerce_to_int`:

```
        # Tuple literals (a, b, c) → hash to int
        if "," in whyml_str and whyml_str.startswith("(") and whyml_str.endswith(")"):
            return str(stable_hash(whyml_str))
```

The key `(y, 1)` lowers to the text `(!y, 1)`, and that TEXT is hashed. Every occurrence of
`(y, 1)` in the function gets the same integer, whatever `y` holds at that point.

## BOTH DIRECTIONS MEASURED at baseline worktree `21d5029e` (source == HEAD `6f36d67f`)

`t_dictkey.py`:

```python
#@ ensures \result == 1
#@ assigns \nothing
def f(x: int) -> int:
    y = x
    d: Dict[Tuple[int, int], int] = {}
    d[(y, 1)] = 5
    y = y + 1
    if (y, 1) in d:
        return 1
    return 0
```

- FALSE `\result == 1` — `[+] Verification SUCCESS` (rc=0). **CPython returns 0** (run).
  Emitted: `d := map_update_some !d 785150688 5` ... `Map.get (!d) (785150688)`.
- TRUE twin `\result == 0` — rc=1, `f'vc` postcondition (read).
- CONTROL `t_dictkey_ctl.py` — the probe key spelled `(y, 2)`: a different text, a different
  hash (`40434288`), the false claim refused. The decision is keyed on SPELLING.

FAIL-CLOSED sibling (logged): a `List[Tuple[int, int]]` literal `[(y, 1)]` is emitted as a
REAL Why3 tuple `Array.make 1 ((!y, 1))` and never reaches this arm.

## WHY #113's REPAIR DOES NOT CLOSE THIS

#113 is a CALL misclassified as a tuple. Here the classification is CORRECT — it is a tuple —
and the defect is the collapse itself. Fixing the classifier leaves this route open.

## REPAIR SKETCH (re-derive before landing)

Map the tuple VALUE, not its text, into the int domain: a POLYMORPHIC UNINTERPRETED logic
function applied to the real Why3 tuple, e.g. `(tuple_key (!y, 1))` with
`function tuple_key (t: 'a) : int`. Congruence gives "equal tuples -> equal keys"; there is NO
injectivity axiom, so two different tuples are merely NOT PROVABLY equal or distinct — sound,
possibly less complete for corpus files that relied on ground-tuple hash distinctness (the
emission diff will say). A ground literal tuple could keep a text hash only if every component
is a literal — and even then, only if hash collisions are accepted as they are for string
literals.
