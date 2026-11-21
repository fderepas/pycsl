r"""Test 2276 — route #242 (expected PASS): CONTROL. A nondeterministic function called ONCE is still
fine: `h` (now a plain `let`) keeps its DECLARED postcondition, which a caller may use, so
`\result >= 0` PROVES. CPython `m()` = 1.
"""
# pycsl-expected: PASS


#@ ensures \result >= 0 and \result <= 1
#@ assigns \nothing
def h(x: int) -> int:
    if isinstance(x, bool):
        return 1
    return 0


#@ ensures \result >= 0
#@ assigns \nothing
def m() -> int:
    return h(True)
