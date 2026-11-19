# CLOSED — ROUTE #45 — CLOSED by relaunch #48 at `49a7334a`. Witnesses `pycsl-reference/1065`-`1069`.
#
# The entry below is kept VERBATIM as the record of how it was found, measured and
# scoped. Everything it says about the DEFECT still holds; everything it says about the
# route being open no longer does.

---

# OPEN ROUTE #45 — `float("nan") == itself` proves, and OPACITY CANNOT FIX IT

**Found 2026-09-08 by relaunch #48, at commit `0f3906bd`. NOT CLOSED — measured, scoped,
and left with its repair named.**

## The demonstration (default `hoare` model, no flags, Python run to confirm)

```python
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = float("nan")
    if x == x:             # Python: `nan == nan` is False -> f() returns 0
        return 7
    return 0
```
`[+] Verification SUCCESS! All contracts formally proven.`

The reproducer is `scratchpad/w48/probe/` (`d8_nan.py`) and `/tmp/w48probe/e1_nan_ne.py`.

## The mechanism, and it is NOT the one the other four singleton routes had

`float(<str>)` has no model, so it lowers to an abstract `val py_float_1 (x0: int) : int` —
an opaque **int**. The emitted guard is then

    x := (py_float_1 244827664);
    if (!x = !x) then ...

and `!x = !x` is **reflexivity of `=`**, which every value model has and which NaN is the
one Python value to break.

**THIS IS WHY THE CAMPAIGN'S STANDING REPAIR DOES NOT APPLY.** Routes #40 (`...`), #41
(erased locals) and #44 (`None`) all closed a wrong-value erasure by making the VALUE
OPAQUE — `val function pycsl_<x> : int` with no defining axiom. That works because those
defects were *comparisons against a known constant*. Here the value is ALREADY opaque, and
it is still equal to itself: an opaque constant satisfies `c = c`. **Opacity is not a fix
for a broken equivalence relation.**

## THE REPAIR IS AVAILABLE AND IT BEATS A REFUSAL, which is unusual for this campaign

NaN's comparison semantics are TOTALLY DETERMINED — every ordering and `==` is False, `!=`
is True, for every operand including itself. So a local bound to `float("nan")` (or
`math.nan`) can lower its comparisons EXACTLY:

| shape | faithful lowering | today |
|---|---|---|
| `x == y` (either side NaN-bound) | `false` | reflexive `=`, DECIDED WRONG |
| `x != y` | `true` | `not (a = b)` |
| `x < y`, `<=`, `>`, `>=` | `false` | opaque int ordering |

That also turns `x = float("nan"); if x != x: return 7` — which Python answers `7` — from
UNPROVABLE into PROVABLE. **The fix is a completeness WIN as well as a soundness one**,
which is the opposite of the usual trade and is the reason to prefer it to a refusal.

## What is already measured, so nobody redoes it

* `f(a: float) -> if a == a` **fails closed** at HEAD: a genuinely `float`-annotated
  operand routes through the `real` comparison path and does not decide reflexivity. The
  defect is confined to the `float(<str>)` constructor's int degeneration.
* `float("inf")`: `x + 1.0 == x` fails closed. Not part of this route.
* `src/pycsl_lib/json/decoder.py` is the only file in the tree that writes `float('nan')` /
  `float('inf')` / `float('-inf')` (three module-level constants). A blanket REFUSAL of
  `float(<non-numeric string>)` would cost exactly that file; the faithful lowering costs
  it nothing.
* EIGHTEEN other shapes were probed in the same battery and every one fails closed:
  `str`/`bytes`/`dict`/empty-`dict`/`set`/`list`/`lambda`/`range`/`enumerate`/`frozenset`/
  class-object/function-object compared to an `int`; `"a" == 1`; `s < 1`; negative
  floor-division and modulo (both literal and through parameters); aliasing through a list
  (`b = a; b[0] = 9; return a[0]`); `try/finally` with a `return` in the `finally`;
  `2 ** -1`; a short-circuit division guard; `**kwargs` / `*args` splats; chained
  assignment; a `global` write; a `nonlocal` capture; `__eq__` / `__len__` / `__bool__`
  overrides; `\result == True` on an int return; `assigns \nothing` with a global read.
