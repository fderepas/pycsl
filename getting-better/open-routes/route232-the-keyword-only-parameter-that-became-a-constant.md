# OPEN ROUTE #232 — THE KEYWORD-ONLY PARAMETER THAT BECAME A MODULE CONSTANT

**Status: OPEN (gen #36, 2026-10-13), Severity 1.** Surfaced by the chain-probe executor while
re-probing `check_imports` (its `*, stub_dir` params were missing from the emitted signature);
driver reproduced in the corpus language at HEAD a6d084e8.

## Witness (PROVED at HEAD; CPython `g()` returns 0)

    #@ ensures True
    #@ assigns \nothing
    def f(*, k: int) -> int:
        return k

    #@ ensures \result == 1
    #@ assigns \nothing
    def g() -> int:
        if f(k=3) == f(k=4):
            return 1
        return 0

## Mechanism
The keyword-only parameter `k` is dropped from the emitted signature (`let function f () : int`),
the body's read of `k` resolves to an auto-declared opaque `val constant k : int`, and both call
sites become `f ()`, so `f(k=3) = f(k=4)` is a theorem. (A contract mentioning `k` is refused —
"Undefined variable 'k' referenced in contract" — which is why it hid: only contract-free uses leak.)

## Repair direction
Emit keyword-only parameters as ordinary parameters (call sites bind keyword actuals by name), or
refuse keyword-only parameters fail-closed. Census corpus + mirror usage first.
