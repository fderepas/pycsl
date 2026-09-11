# OPEN ROUTE #61 — A DICT LITERAL WITH **NON-CONSTANT** KEYS STILL TAKES THE SYNTACTIC COUNT
# (found 2026-09-11 by relaunch #55, at `11cc83f8`)

## THE HEADLINE

    #@ requires a == b
    #@ ensures \result == 2
    def f(a: int, b: int) -> int:
        d: Dict[int,int] = {a: 1, b: 2}
        return len(d)            # CPython: 1.  `\result == 2` **PROVES**.

BOTH DIRECTIONS MEASURED: the FALSE claim proves; the TRUE twin (`== 1`) times out and does
not prove. Unsound in the SILENT direction. The emission carries the same signature route
#60 was found by — **`warning: unused variable d`** — the length is a constant and the map
is never consulted.

Note the precondition does the work: `requires a == b` makes the collision a FACT the prover
has, and it still answers 2. No solver cleverness is needed to see the contradiction; the
fold simply never asked.

## THIS IS THE THIRD PATH TO ONE SEMANTICS. THE FIRST TWO ARE CLOSED.

  * **ROUTE #54 (closed)** — a dict LITERAL with equal-but-differently-spelled CONSTANT keys
    (`{1: 10, True: 20}`). Its repair gave the literal fold *Python's own key equality*, but
    only for keys it can normalise to a value.
  * **ROUTE #60 (closed, this generation)** — a dict SUBSCRIPT STORE (`d[1] = 2`). Its repair
    whitelisted the store tracker.
  * **ROUTE #61 (this file)** — the LITERAL again, with keys that are NAMES rather than
    constants. `#54`'s normalisation returns "not a literal" and the code falls back to
    `len(keys)`, the raw syntactic count.

**IT IS DOCUMENTED — AND THAT IS THE POINT.** `docs/pycsl-translational-reference.md` states
it as a *"Stated residue: a dict literal with a NON-CONSTANT key (13 in the mirror, 2 in the
corpora) still takes the syntactic count, because two variables may be equal and the fold
cannot know."* The reasoning is correct and the conclusion drawn from it is not: **"the fold
cannot know" is an argument for REFUSING, not for guessing.** A residue that PROVES A FALSE
CLAIM is a soundness route, not a boundary — a boundary fails closed. This is what the
campaign's documented-claim audit was built to find.

## THE DEFECT IS ONE EXPRESSION

`src/pycsl/module6_whyml/types.py`, the `DictLit` branch of `_track_collection_metadata`:

```python
    self._known_collection_sizes[target] = (
        len(set(_r54_norm)) if _r54_norm is not None else len(keys))
```

`_r54_norm` is `None` exactly when some key is not a literal. The `else len(keys)` is the
route. Registering NOTHING in that case makes `len(d)` fall through and fail closed, which is
what every other unfoldable dict `len` already does.

## WHAT IS NOT YET MEASURED

  1. The blast radius of refusing. The docs claim 13 such literals in the MIRROR and 2 in the
     corpora — but a literal only matters here if `len()` is actually taken of it, which is a
     much smaller set. MEASURE, do not trust the count: mirror emission (53/53), mirror
     type-only, and a byte-diff over BOTH corpora.
  2. Whether the ELEMENT fold (`d[k]`) has the same hole for non-constant keys — route #54
     had two victims, `len(d)` AND `d[1]`, and only the size half is probed here.
  3. The SET and LIST literal analogues.
