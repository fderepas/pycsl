r"""Test 1713 — ROUTE #207: `#@ no_exception \all` proved for a method whose body is a call
to a `\trusted` method that always raises.

Route #161 inverted the default for `no_exception` callees: a call is allowed only if the
callee is "a function or class of the verified program (its own contract speaks for it)"
or on a short whitelist of operations that cannot raise. A `\trusted` / `\abstract` callee
IS a function of the program, and what speaks for it is an ASSUMPTION — no body is
lowered, and a bodyless `val` carries no `raises`, so Why3 is told the call cannot raise.

THE TOOL DISAGREED WITH ITSELF ABOUT THE SAME PROGRAM. This file PROVED. The MODULE-LEVEL
twin — a `\trusted` module function `boom` raising ValueError, called from a
`no_exception \all` module function — was already REFUSED, and so was this same class with
an UNtrusted raising `boom` (its body's `raise` propagates and the caller FAILS). Only the
trusted METHOD slipped through, admitted by route #161's method arm on the strength of its
NAME.

CPython: `Box().safe(1)` raises ValueError. Control: 1714.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


class Box:
    #@ ensures \result >= 0
    #@ \trusted
    def boom(self, n: int) -> int:
        raise ValueError("always")

    #@ requires n >= 0
    #@ no_exception \all
    #@ ensures \result >= 0
    def safe(self, n: int) -> int:
        return self.boom(n)
