# OPEN ROUTE #241 — A GENERATOR ACTUAL TO AN `Any` PARAMETER IS THE LITERAL `0`

**Status: OPEN (gen #36, 2026-10-15), Severity 1.** Recorded as a residual by the #239 repair executor;
driver-reproduced at HEAD ab2c2d4f (rc=0 "Verification SUCCESS"; CPython `m()` = 0).

## Witness
`witnesses-r241/genexp_actual_is_zero.py`: `g(x: Any)` with `ensures x == 0 ==> \result == 1`;
`m()` returns `g(v for v in [1])` with `ensures \result == 1` PROVES. Emission: `g 0`.

## Mechanism
Route #41's generator erasure (a generator value lowered to the literal `0`), one position over: a call
ACTUAL rather than a local binding (#239 made the local-binding form a fresh `(any int)`).

## Repair direction
An erased generator (or any erased value) in actual position must be a fresh `(any int)` (or refused),
never a definite constant. Census other erased-value-as-constant sites in actual / return / field-store
positions.
