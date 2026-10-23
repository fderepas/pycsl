r"""Test 1835 — ROUTE #222 CONTROL (expected FAIL): the `ensures` path still works.

Route #222's refusal must be about the clauses that were DISCARDED, not a ban on `#@` on an
`@overload` stub. This file keeps the documented path exercised: the stub's
`#@ ensures \result == 99` becomes a guarded postcondition on the implementation, whose body
returns 1 — so the file FAILS, and it fails on that synthesized obligation rather than on a
refusal. If this file ever starts being REFUSED, the repair has become a ban on the feature.

It is also the FIRST corpus file to exercise `@overload` at all: the construct had an
implementation (`_is_overload_stub`, `_synthesize_overload_guard`,
`_build_overload_param_guard`), a documented lowering, and ZERO corpus witnesses.
"""
# pycsl-expected: FAIL
from typing import overload
_ = 0  # anchor


#@ ensures \result == 99
@overload
def f(x: int) -> int: ...


#@ ensures \result == 1
def f(x: int) -> int:
    return 1
