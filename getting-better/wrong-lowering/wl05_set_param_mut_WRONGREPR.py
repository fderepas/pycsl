"""WL-05b FIXED (was WL-05 set twin) — now PROVEN: an in-place `s.add(x)` on a Set
PARAMETER is modelled as a caller-visible mutable `ref (map …)` with a `writes {s}`
frame, so the mutation escapes and proves faithfully. Historical note (repro record):
an in-place mutation `s.add(x)` of a Set PARAMETER is the
same class as the dict `d[k]=v` param write: Python mutates the set BY REFERENCE,
so the caller must see it, but PyCSL's by-value `map int (option int)` param carries
no `writes {s}` frame. The old lowering silently DROPPED the mutation to a no-op
(sound but UNFAITHFUL — a caller-visible write vanished). Now REJECTED with a clear
diagnostic (verdict REJECTED), mirroring the dict param write and the record/list
param-mutation boundary. A LOCAL set add-membership IS faithful (proves)."""
_ = 0
from typing import Set
#@ ensures \result >= 0
def f(s: Set[int]) -> int:
    s.add(5)
    return 0
