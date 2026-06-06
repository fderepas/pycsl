**Bounded quantification** is a quantifier that ranges over the members of a
collection — `\forall x: T in S; P` ("every element of set `S` satisfies `P`") and
its existential dual `\exists x: T in S; P`.

---

## Desugaring

It is sugar for a membership-guarded ordinary quantifier (no new emission):

```
\forall x: T in S; P    ≡    \forall x: T; (x in S) ==> P
\exists x: T in S; P    ≡    \exists x: T; (x in S) and  P
```

reusing the typed binder, the `in` membership, and implication/conjunction.

## Why the membership form matters

For a **set** `S` (modeled as `map int (option int)`), `x in S` lowers to clean
*key* membership `Map.get S x` — not a positional sequence search. That term
e-matches: given a hypothesis `k in S`, the solver instantiates the bound universal
at `k` automatically, **no trigger needed**.

```python
#@ requires \forall x: int in s; x >= 0
#@ requires k in s
#@ ensures \result >= 0
def pick(s: set, k: int) -> int:
    return k                          # k >= 0 by instantiation at the member k
```

Bounding over a *list* uses positional (`exists i. 0 <= i < len /\ xs[i] = x`)
membership, whose nested existential does **not** e-match — that case may need a
trigger (deferred).

## Relation to other quantifier forms

Part of the quantification feature set: typed binders (`\forall x: T`), bounded
binders (this), **multi-binder** sugar (`\forall x, y;` → nested), and **class
binders** (`\forall o: C;`, where the `#@ class invariant` holds for every `o` via
the Why3 type invariant). Driver `0568`. See `test-suite/annotations.md` §3.3.
