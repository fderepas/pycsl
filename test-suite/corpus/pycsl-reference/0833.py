"""Test 0833 — WL-05b regression lock (POSITIVE, set twin of 0832): set-PARAM add ESCAPES to the caller.

wrong-lowering-to-fix.md §WL-05b (caller-visibility, set). `add_it` takes
`s: Set[int]`, mutates it (`s.add(7)`) and states the observable post-state in its
contract (`#@ ensures 7 in s`, i.e. `Map.get !s 7 <> None` after the `writes {s}`
frame). `caller` allocates a LOCAL set `s` (a `ref`), calls `add_it(s)` — the call site
passes the bare ref so the mutation escapes — and reads back the membership `7 in s`,
which the callee's `ensures` proves. Returns `1` — the observable CONSEQUENCE of the
caller-visible set mutation.
"""
_ = 0  # anchor
from typing import Set


#@ ensures 7 in s
def add_it(s: Set[int]) -> None:
    s.add(7)


#@ ensures \result == 1
def caller() -> int:
    s: Set[int] = set()
    add_it(s)
    if 7 in s:
        return 1
    return 0
