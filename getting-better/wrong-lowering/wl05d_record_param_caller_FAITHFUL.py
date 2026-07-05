"""WL-05d (T8) — the record-param field mutation ESCAPES to the caller (verdict PROVEN).

`caller` calls `setx(p)` (which sets `p.x = 5`); the caller observes the write via the
callee's `ensures p.x == 5`. Confirms the mutation is caller-visible (Why3-inferred
`writes {p.x}` propagates through the call), the by-reference semantics of Python objects."""
_ = 0
from dataclasses import dataclass
@dataclass
class Point:
    x: int
    y: int
#@ ensures p.x == 5
def setx(p: Point) -> None:
    p.x = 5
#@ ensures p.x == 5
def caller(p: Point) -> None:
    setx(p)
