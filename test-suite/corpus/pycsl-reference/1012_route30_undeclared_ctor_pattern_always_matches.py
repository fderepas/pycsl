"""Test 1012 — ROUTE #30, second mechanism: an UNDECLARED constructor pattern
becomes a Why3 VARIABLE PATTERN, which matches every subject.

FALSE OF THE PROGRAM: `x` is 5, an int never matches `str()`, and Python
returns 2.

At the parent commit c4233fed this printed `[+] Verification SUCCESS!`. The
match had a `Constructor` arm, so it took the NATIVE Why3 match path
(`_render_match_pattern`), which wrote the constructor name verbatim:

    match x with | str -> 1 | _ -> 2

Why3 reads a lowercase identifier that is not a known constructor as a fresh
VARIABLE binder — an irrefutable catch-all. A pattern is only a pattern if its
head is a constructor the emission DECLARED, which is now checked against
`self._constructors` (`PYCSL-R30-UNDECLARED-CTOR-PATTERN`). A `case Just(n)` on
a real `#@ datatype` is unaffected — see 0540 and 1003.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires x == 5
#@ ensures \result == 1
#@ assigns \nothing
def f(x: int) -> int:
    match x:
        case str():
            return 1
        case _:
            return 2
