# OPEN ROUTE #64 — `no_exception \all` PROVES FOR A PROGRAM THAT RAISES `ValueError`
# (found 2026-09-11 by relaunch #55, at `73972e49`)

## THE HEADLINE

```python
#@ no_exception \all
#@ ensures \result == 999
#@ assigns \nothing
def f() -> int:
    b = bytearray([1])
    b[0] = 999
    return b[0]
```

**`[+] Verification SUCCESS! All contracts formally proven.`**
CPython raises **`ValueError: byte must be in range(0, 256)`**.

`#@ no_exception ValueError` — naming the exact exception that is raised — proves too.

**THIS IS NOT A PARTIAL-CORRECTNESS CAVEAT.** An `ensures` on a raising program can be
excused as vacuous under partial correctness; `no_exception` cannot. It is a POSITIVE claim
about runtime behaviour — "no IR operation in this body can raise a listed exception" — and
`\all` is the strongest form of it, expanding to the entire modelled set. `ValueError` IS in
`exception_model.KNOWN_EXCEPTIONS`, so this is a claim PyCSL explicitly offers to prove, and
it proves it wrongly.

## THE MECHANISM WORKS — MEASURED BOTH WAYS, WHICH IS WHAT MAKES THIS A GAP AND NOT A NO-OP

  * `a // 0` under `#@ no_exception ZeroDivisionError` — **does NOT prove.** Correct.
  * `a // b` under `#@ no_exception ZeroDivisionError` with `requires b != 0` — **PROVES.**
    Correct.

So the machinery discharges real obligations. It is simply SILENT here: the trigger table
`exception_model.IMPLICIT_TRIGGERS` has exactly three `ValueError` entries — `binop <<`,
`binop >>` (negative shift counts) and `attr_call index`. **There is no entry for a
`bytes`/`bytearray` ELEMENT STORE.** No trigger means no `assert`, and `\all` then ranges
over a set of obligations that does not include the one this program violates.

## THE DOCUMENTED GUARANTEE THIS BREAKS, AND THE HALF-TRUE JUSTIFICATION BEHIND IT

`docs/pycsl-translational-reference.md` (§WL-06c):

> "a byte cannot hold a value outside [0,256); an out-of-range byte cannot be constructed).
> This is a **TYPE-LEVEL guarantee**, so PyCSL EMITS it as an IMPLICIT precondition"

justified by:

> "it is never violated in-body because **no `bytes`/`bytearray` PARAMETER element write is
> emitted**"

**THE JUSTIFICATION IS ABOUT PARAMETERS AND THE GUARANTEE IS STATED ABOUT BYTES.** A LOCAL
`bytearray` element write IS emitted and IS faithful — measured: `b = bytearray([1,2]);
b[0] = 9; return b[0]` proves `\result == 9` (CPython's answer) and the stale `== 1` does
not prove. So the write the justification says cannot happen in-body happens in-body, for a
local, and carries any integer at all.

## THE STATE IS NOT CONTRADICTORY — CHECKED, BECAUSE IT WOULD HAVE BEEN MUCH WORSE

If the byte-range invariant were ASSUMED for a local after such a write, the proof state
would be inconsistent and would prove anything. It is not: after `b[0] = 999`, neither
`\result == 0` (absurd) nor `\result < 256` (the invariant) proves. The invariant is simply
not carried for locals. So the damage is confined to the missing exception trigger.

## EXTENT, MEASURED

  * `bytearray` local element store, value out of range, under `no_exception \all` or
    `no_exception ValueError`: **BROKEN** (the headline).
  * `bytes` (immutable) local element store: the false claim does NOT prove.
  * The `bytearray` store VALUE itself is faithful — this is not a value-model route.

## THE REPAIR SHAPE

Add the missing trigger rather than refusing the construct: an element store to a
`bytes`/`bytearray` receiver raises `ValueError` unless `0 <= v < 256`. That is exactly what
`IMPLICIT_TRIGGERS` is for, it makes `no_exception` discharge or fail honestly, and it bites
ONLY on programs that opt in to `no_exception` — so it should be inert on everything else.
