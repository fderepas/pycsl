"""WL-05d (T8) — the severity-1 fail-OPEN that was FIXED (verdict UNPROVEN; was Valid).

Before WL-05d, `p.x = 5` on a record PARAMETER was silently DROPPED by Module 5 (no IR
emitted) → a no-op: `requires p.x == 3` then `ensures p.x == 3` (claiming the field is
UNCHANGED after a real mutation to 5) proved Valid on BOTH Alt-Ergo and Z3 — an UNSOUND
false green (real Python has p.x == 5). Now the store lowers to `p.x <- 5`, so the claim
FAILS. This driver locks the fix: it must stay UNPROVEN forever."""
_ = 0
from dataclasses import dataclass
@dataclass
class Point:
    x: int
    y: int
#@ requires p.x == 3
#@ ensures p.x == 3
def setx(p: Point) -> None:
    p.x = 5
