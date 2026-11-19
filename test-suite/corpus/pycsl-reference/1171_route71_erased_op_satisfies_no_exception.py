"""1171 — ROUTE #71 NEGATIVE: an ERASED operation trivially satisfies `no_exception`.

`t.remove(5)` on a collection PARAMETER inside a `@mutable_state` class lowers to `()` —
the documented no-op. The exception model injects obligations at EMISSION SITES, so an
operation that is not emitted cannot carry one, and `#@ no_exception \all` discharged over a
body whose emitted form is literally `(); 0`. CPython raises `KeyError: 5`.

This inverts the usual reading of an erasure: a dropped mutation is argued fail-closed
because the POST-STATE claim becomes unprovable — but for `no_exception` the erasure makes
the claim EASIER.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from dataclasses import dataclass, field
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    s: Set[int] = field(default_factory=set)

    #@ requires True
    #@ no_exception \all
    #@ ensures True
    #@ assigns \nothing
    def probe(self, t: Set[int]) -> int:
        t.remove(5)
        return 0
