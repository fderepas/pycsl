# Route #199 — the empty f-string was the integer zero

**Status:** CLOSED (gen #30). SEV-1. Decisive signature present. **The first FAITHFUL repair
of the generation** — the true contract is provable after it, not merely undecided.

## The claim that was wrong

`src/pycsl/module6_whyml/expressions.py::_handle_fstring_expr`:

```python
parts = expr.get("parts", [])
if not parts:
    return "0"
```

The very next arm lowers an all-string f-string to a faithful Why3 `string` concat chain.
The EMPTY one — `f""`, which is the empty string — answered the integer `0`.

## The witness

```python
#@ ensures \result == 2
def probe() -> int:
    s = f""
    if s == "":
        return 1
    return 2
```

PROVED. CPython answers 1 (`f"" == ""` is True). The TRUE twin `\result == 1` was REFUSED.

Corpus: `1695_route199_the_empty_fstring_was_the_integer_zero.py` (expected FAIL),
`1696_route199_the_empty_fstring_is_the_empty_string.py` (the completeness witness, PASSES).

## The repair, and the one it replaced

The obvious repair — `return '""'` — is WRONG, and the emitted WhyML is what said so:

```
let s = ref 0 in
s := "";
if (!s = 313406155) then ...
```

an `int` ref assigned a `string`. Fail-closed, but by a TYPE ERROR rather than by an
answer, and the true contract stayed refused. The cause is upstream: BOTH `_is_string_expr`
FString arms gate on `bool(parts)`, so an empty f-string is not string-typed and its local
is declared `ref 0`.

In the int-hash string model the empty string IS `stable_hash('""')` — 313406155, the very
constant the comparison already emits. So:

```python
return str(stable_hash('""'))
```

closes the false proof AND makes the true contract provable, with no type change anywhere.

**Recorded not taken:** make the empty f-string string-typed (drop `bool(parts)` from both
`_is_string_expr` arms — `all([])` is already True — and return `""`). Three sites in a
predicate every consumer reads, for a construct with zero occurrences in the corpus, in
`src/pycsl/`, in `src/self-annotate/src/` or in `src/pycsl_lib/`. It belongs with the next
f-string typing change, not with a soundness fix.

## Why the completeness witness exists

`1696` is not decoration. A later "simplification" of this repair to an opaque would still
pass `1695` and would silently lose the true contract. The pair pins BOTH directions.

## Prediction vs measurement

| | predicted | measured |
|---|---|---|
| `\result == 2` (false) | REFUSED | REFUSED |
| `\result == 1` (true twin) | PROVES | PROVES (after the repair was re-aimed) |
| corpus byte-diff | ZERO | ZERO (`0 MOVED, 0 GONE, 0 APPEARED`, 2 new sources ignored) |
| mirror emission byte-diff | ZERO | ZERO — byte-inert in all three directions |

The mirror's `_handle_fstring_expr` is a re-trusted stub, so the live edit has no mirror
twin and mirror-sync is unaffected.
