# OPEN ROUTE #68 — TWO MORE LOWERED OPERATIONS WITH NO TRIGGER ROW
# (found 2026-09-11 by relaunch #55, at `a97da69e`)

## THE CARRIERS — both `[+] Verification SUCCESS` under `#@ no_exception \all`

```python
    x = float("abc")      # CPython: ValueError: could not convert string to float
    return 0 ** (-1)      # CPython: ZeroDivisionError: 0.0 cannot be raised to a negative power
```

Both lower to OPAQUE abstract operations with no `ensures` at all, so neither is a false
axiom — but neither carries an exception obligation either:

    float("abc")  ~>  val py_float_1 (x0: int) : int
    0 ** (-1)     ~>  val function py_pow (x: int) (y: int) : int

**NOTE WHAT `float("abc")` DOES TO ITS ARGUMENT.** The emitted call is
`py_float_1 1824800645` — the STRING WAS HASHED TO AN INT before being handed to an
opaque val. The argument is not merely unmodelled; it is gone. (That is the documented
string-hash path, not a new defect, but it is why no condition over the string is available
at this site and why refusal is the only honest repair here.)

## THE CONTROL, MEASURED IN THE SAME BATCH

`a % (a - a)` under `#@ no_exception \all` — **does NOT discharge.** The `("binop", "mod")`
row is wired and bites on a symbolic zero divisor. So the machinery is working and these two
operations are simply outside it.

## THIS IS THE FIFTH AND SIXTH CARRIER OF ONE PATTERN

Routes #64, #65, #66, #67 and now #68 are all the same underlying fact: **nothing relates
`exception_model.TRIGGERS` to the set of operations the emitter actually lowers.** Found so
far, each by a separate probe:

| operation | exception | state before |
|-----------|-----------|--------------|
| `bytes`/`bytearray` element store | `ValueError` | no row (#64) |
| `divmod`, `.index`, `.pop`, `next` | various | rows present, consulted by NOTHING (#65) |
| `del d[k]`, `int(<str>)`, `chr(n)` | `KeyError`/`ValueError` | no row (#66) |
| string subscript read | `IndexError` | no row (#67) |
| `float(<str>)`, `**` | `ValueError`/`ZeroDivisionError` | no row (#68) |

**PATCHING ONE OPERATION AT A TIME IS NOT CONVERGING.** Six probes, six findings. The
honest reading is that `#@ no_exception \all` currently means "none of the exceptions this
table happens to model", and the gap between that and what the directive SAYS is the real
defect. The completeness gate named in route #66 — enumerate what the emitter LOWERS and
check each has a row — is worth more than any further individual repair.

## THE REPAIR SHAPE

  * `float(<str>)` — **REFUSE** under a `ValueError` context. The argument is hashed away, so
    there is no faithful condition to inject; same posture as `int(<str>)`.
  * `**` — **WIRE** it. Python raises `ZeroDivisionError` exactly when the base is `0` and the
    exponent is negative, and BOTH operands are available at the call site, so the condition
    `not (base = 0 /\ exp < 0)` is exact and a correct program still discharges.

## STATUS: **CLOSED** — AND IT GREW A THIRD CARRIER THAT WAS A DEAD ROW, NOT A MISSING ONE

| carrier | CPython | repair |
|---------|---------|--------|
| `0 ** (-1)` | `ZeroDivisionError` | **WIRED** — new `("binop","**")` row, `not (base = 0 /\ exp < 0)` |
| `1 << (-1)` | `ValueError` | **WIRED** — the `("binop","<<")`/`(">>")` rows existed ALL ALONG and were never injected |
| `float(<str>)` | `ValueError` | **REFUSED** — the string is hashed to an int before reaching the opaque val |

**THE SHIFT CARRIER IS THE INTERESTING ONE, AND IT IS A FAILURE OF THE PLANE I ADDED HOURS
EARLIER.** `non_neg_shift` has been in the table for a long time. `check-trigger-rows-live`
reported it live — because ONE binop site (`div`/`mod`) passes a DYNAMIC op-key
`("binop", raw_op)`, and the plane approves a whole KIND from a dynamic key. The bitwise and
power emission path is a DIFFERENT site and it did not wrap, so the shift rows were never
injected and `1 << -1` proved.

**THE KIND-LEVEL APPROVAL IS THE PLANE'S SHARPEST LIMIT**, and it is now documented in the
plane itself. The fix was to make the ASSUMPTION TRUE — the bitwise/power path now wraps —
rather than to weaken the check. If a new binop emission path is added and does not wrap,
that approval silently starts lying again.

### GATES
All 32 planes green; mirror 53/53 type-clean and byte-inert; both corpora byte-inert; metric
unchanged at 459. Witnesses `1162`/`1163`/`1165` (negatives, each anti-vacuity-verified in
both directions) and `1164` (positive control: a valid `**` and `<<` still discharge).
