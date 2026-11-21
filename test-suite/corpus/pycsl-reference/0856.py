"""Test 0856 — WL-05c (T7) regression lock (NEGATIVE): `del d[k]` on a dict METHOD
parameter is REJECTED. # pycsl-expected: FAIL

wrong-lowering-to-fix.md §WL-05c. A dict/set METHOD param that is item-mutated (here via
`del d[k]`) keeps the WL-05 boundary: its param type also feeds the abstract-op
call-contract map that models `obj.m(d)` at every call site, which the caller-visible
`ref (map …)` promotion would desync. So a method `del d[k]` is REJECTED (clean
PyCSLError) rather than silently no-op'd. This is ALSO the fix for the severity-1
fail-OPEN: before WL-05c the method `del` proved a false "key survives" claim. Must NOT
verify ⇒ XFAIL."""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Dict


class Box:
    def __init__(self) -> None:
        self._n = 0

    #@ ensures True
    def rm(self, d: Dict[str, int]) -> None:
        del d["a"]
