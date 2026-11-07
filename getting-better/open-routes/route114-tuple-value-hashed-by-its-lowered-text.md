# ROUTE #114 — a TUPLE in an int position (a dict key) is replaced by a HASH OF ITS LOWERED
# TEXT, so `(y, 1)` is the SAME key before and after `y` changes

**Status: CLOSED AND FULLY GATED by gen #23 (2026-09-15)** — see THE REPAIR AS LANDED at the bottom. Original finding preserved below.
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

---

# THE REPAIR AS LANDED — gen #23 (2026-09-15)

Landed with routes #111–#117 as ONE combined battery (commit recorded in `driver-progress.log`).
Every verdict was PREDICTED in the progress log before it ran:
metric 459/484/25/0 · doc-coherency rc=0 · mirror sync 887 verbatim · mirror-check same 3
pre-existing drifts · trusted-raises 13/62 · trusted-reasons 459↔459 · type-only 53, 0
ill-typed · dropped-mutation 0/51/9/0 · byte-diff pycsl-ref 22 MOVED / GONE only 0996 (an
expected-FAIL witness now refused) · python-ref 6 MOVED · mirror emission 7 MOVED, every hunk
read and attributed · suite 3444/3462, the SAME 18 failures, ZERO XPASS · whole-file proofs of
all 7 moved mirrors SUCCESS, 0 bad (statements 17630, expressions 21347, stmt_control_flow
12284, pure_ast 3372, functions 1199, Module5_IREmitter 2109, preamble 216 Valid) · planes
34/34 `ok` COUNTED (after narrowing `check-singleton-constant-lowering`'s baseline: the split arm orphaned two entries whose justifications #115/#116 had just refuted — removed — and renamed the GenExp half's key; constant arms 14 -> 12; emission re-verified byte-identical).

**What landed.** In the same arm, a GENUINE tuple in an int position becomes Why3 `(any int)` —
unknown, never a hash of its text. A value-keyed uninterpreted `tuple_key` was drafted first and
dropped: it needs an abstract-op declaration, and `_coerce_to_int`'s PROVED mirror is
`assigns \nothing`. **Measured completeness cost:** `d[(y, 1)] = 5; (y, 1) in d` (true) is no
longer provable. Census: 9 genuine-tuple sites in all trees (python-reference 0150, 3 mirror,
5 pycsl_lib), no corpus verdict moved. Corpus 1312 (XFAIL).
