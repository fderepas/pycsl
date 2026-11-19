# Route #202 — the same hash, through a parameter with NO annotation

**Status:** CLOSED (gen #30). SEV-1. Decisive signature present. **This is the residue route
#200's own repair note wrote down**, found by reading that note back an hour later.

## The claim that was wrong — my own, from one route earlier

Route #200 refuses a string literal actual against a parameter **declared** `int` / `bool` /
`float`, and its note explains why the declared key is the right one:

> The 46 sites where a string literal reaches an `int` param across the 53 mirror emissions
> are `int` BY ERASURE (the callee's parameter carries no annotation at all). The witness's
> parameter is `int` BY DECLARATION …

That is true, and it is what made #200 free. It is also exactly the hole: **a parameter with
no annotation is erased to `int` by the emitter and gets the same `stable_hash`
substitution.**

## The witness

```python
#@ requires True
#@ ensures p == 747471683 ==> \result == 1
#@ ensures p != 747471683 ==> \result == 2
def callee(p) -> int:            # NO annotation
    if p == 747471683:
        return 1
    return 2

#@ ensures \result == 1
def probe() -> int:
    return callee("a")
```

Emitted `(callee 747471683)`; `\result == 1` PROVED. CPython answers 2. The TRUE twin
`\result == 2` was REFUSED.

Corpus: `1701_route202_a_string_actual_hashed_into_an_unannotated_param.py` (expected FAIL),
`1702_route202_an_unread_unannotated_param_still_takes_a_string.py` (control, PASSES).

## The axis the repair keys on, and why it is not the annotation

**The hash is only dangerous when a contract can READ the parameter.** An erased parameter
whose callee says `ensures True` cannot decide anything, whatever the model substitutes —
that is the shape all 46 mirror sites have. So the un-annotated case is refused **only when
the callee's own `requires`/`ensures` mentions that parameter**, which is the exact
soundness condition rather than a proxy for it.

The declared-scalar rule from #200 is **not** narrowed by this: it still fires whether or
not the contract mentions the parameter. The change is strictly *more* refusals than the
tree had before it, never fewer.

## The lesson this one is really about

#200's note is a good note: it states the scope, gives the measurement behind it, and names
the population it excludes. The population it names **is** the hole, and the note was
written by the same worker, in the same hour, and read back one route later.

> A RESIDUE YOU WRITE DOWN IS A WORK ITEM, NOT AN EXCUSE. Reading your own scope note back
> and asking "so what does this scope let through?" is the cheapest route-finding move in
> the campaign — it cost one `pycsl.py` run here.

## Prediction vs measurement

| | predicted | measured |
|---|---|---|
| the witness | REFUSED | **REFUSED** (`PYCSL-SEM-STRARG`) |
| the TRUE twin | also refused | **also REFUSED** |
| control `1702` | still VERIFIES | **VERIFIES** — after being rewritten: its first version used `ensures True`, so the refusal correctly did not fire but the caller could not prove anything either. A control that fails for the wrong reason proves nothing. |
| corpus + mirror byte-diff | ZERO | corpus: 2 GONE (the two intended new refusals, declared with `--expect-gone`) + 1 MOVED (my own edit to witness 1702's contract); **no pre-existing program moved**. Mirror: **ZERO**. |
