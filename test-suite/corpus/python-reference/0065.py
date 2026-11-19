"""Test 0065 — Python Reference 3.2.12: I/O objects (also known as file objects)

(#49) ROUTE #84 — THIS FILE IS NOW AN EXPECTED FAILURE, AND THE REFUSAL IS THE POINT.

Its assertion is `assert buf.read() == "hello"`, and `read()` ADVANCES THE STREAM POSITION.
A Python `assert` was lowered to `()` — the test DISCARDED — so that mutation was ERASED
while the assertion itself still SUCCEEDS and the function runs to completion. That is
route #84: an erased effect inside a passing assert, in a program that stays TOTAL.

Measured on the same mechanism: `xs = [1, 2, 3]; assert xs.pop() == 3; return len(xs)`
proved `\result == 3` while Python returns 2, the true twin was refused, and the stale
length DISCHARGED a callee's `requires`. **And the same `xs.pop()` written OUTSIDE an
assert is REJECTED by this build** — so the assert was carrying a refused construct past
its own guard, which is strictly worse than an unmodelled operation.

`Module6_WhyMLTranspiler`'s assert arm now refuses a test whose calls cannot be shown
effect-free (`PYCSL-M6-ASSERT-EFFECTFUL-TEST`). A PURE test still lowers exactly as
before: `assert n > 0`, `assert len(xs) == 3`, a call to a function with
`#@ assigns \nothing`, and a call to a trivially-pure `def f(x): return x` all still
prove. This file is the ONE corpus casualty out of the whole reference suite, and it is
the genuine hazard rather than a collateral one — the guard was narrowed from NINE
newly-refused files to this one after measuring that the other eight were programs this
build handles correctly.

Marked `pycsl-expected: FAIL` rather than left as an untracked failure so that the XPASS
rule GUARDS it: if this file ever starts proving again, route #84 has reopened and the
suite will say so.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 0
def test_io_objects() -> int:
    """I/O objects (file objects) support read/write."""
    import io
    buf = io.StringIO("hello")
    assert buf.read() == "hello"
    return 0

if __name__ == "__main__":
    assert test_io_objects() == 0
