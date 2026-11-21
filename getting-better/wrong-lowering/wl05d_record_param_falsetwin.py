"""WL-05d (T8) — FALSE TWIN: after `setx(p)` overwrites `p.x` to 5, a caller must NOT be
able to prove `p.x` UNCHANGED (verdict UNPROVEN — the soundness oracle).

`caller` requires `p.x == 3`, calls `setx(p)` (sets p.x to 5), then claims `ensures p.x == 3`
— FALSE of real Python. If this PROVED, the `writes {p.x}` frame would be missing (a caller
assuming a stale post-state) = the severity-1 fail-OPEN. It must stay UNPROVEN."""
_ = 0
from dataclasses import dataclass
@dataclass
class Point:
    x: int
    y: int
#@ ensures p.x == 5
def setx(p: Point) -> None:
    p.x = 5
#@ requires p.x == 3
#@ ensures p.x == 3
def caller(p: Point) -> None:
    setx(p)
