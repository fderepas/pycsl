# Route #201 — a string actual became a ONE-ELEMENT array

**Status:** CLOSED (gen #30). SEV-1. Decisive signature present.

## The claim that was wrong — the same docstring route #193 half-corrected

`src/pycsl/module6_whyml/expressions.py::_array_coerce_arg` opens with

> A length-1 placeholder array works because the abstract vals have no axioms about their
> input contents.

Route #193 falsified the first half of that: the defence is about CONTENTS and says nothing
about LENGTH, and `sorted_1` carries `ensures { Array.length result = Array.length a }`. It
repaired the `stripped == "0"` case to `(any (array int))` and **left the function's TAIL**:

```python
# Anything else (BinOp result, parenthesised int expression) —
# coerce to placeholder since we can't recover the array.
return "(Array.make 1 0)"
```

Route #201 falsifies the second half: the defence also assumes the only consumers are the
emitter's own abstract vals. A **user-declared `List[int]` parameter** reaches the same
coercion.

## The witness

```python
#@ requires True
#@ ensures len(p) == 1 ==> \result == 1
#@ ensures len(p) != 1 ==> \result == 2
def callee(p: List[int]) -> int:
    if len(p) == 1:
        return 1
    return 2

#@ ensures \result == 1
def probe() -> int:
    return callee("ab")
```

Emitted `(callee (Array.make 1 0))`; `\result == 1` PROVED. CPython: `len("ab")` is 2, so
`callee("ab")` returns **2**. The TRUE twin `\result == 2` was REFUSED.

A string literal reaches the tail because it is none of the cases above it: not `"0"`, not
array-shaped, and not alphanumeric once the quotes are counted.

## The spellings, measured

| actual | emission | verdict |
|---|---|---|
| `callee("ab")` | `(Array.make 1 0)` | **THE ROUTE** — CPython returns 2, the model proves 1 |
| `callee(1 + 1)` | same placeholder, also proves | a wrong value, but CPython raises `TypeError` on `len(2)`, so it is not a false proof about a TOTAL program |
| `callee((2))` | — | REFUSED |
| `callee(len([1, 2]))` | — | REFUSED |
| `callee(5)` | — | REFUSED, and by a TYPE ERROR (the bare-identifier pass-through hands `5` where `array int` is expected), not by design |

## The repair

The tail answers `(any (array int))`, the device route #193 introduced one arm above —
declaration-free, so the function stays a pure `@staticmethod` and its mirror stays a
CONVERTED method with `assigns \nothing` (this is the shape #193 first got wrong by
declaring an abstract val, which made the method effectful and turned three fidelity planes
red). The docstring's defence is rewritten rather than deleted: both halves of it were
false, and each half was measured.

## Prediction vs measurement

| | predicted | measured |
|---|---|---|
| `\result == 1` (false) | REFUSED | see the battery record in `driver-progress.log` |
| `\result == 2` (true twin) | REFUSED (opaque answers neither) | " |
| `callee(1 + 1)` | REFUSED | " |
| corpus byte-diff | ZERO — the tail fires **0 times across all 1624 pycsl-reference files**, censused before the repair | " |
| mirror emission byte-diff | measured, not assumed — the mirror is where this coercion's real users live (`sorted_1`, `any_1`, `all_1`, `array_rev`, `array_to_seq`, the field-decode idiom) | " |
