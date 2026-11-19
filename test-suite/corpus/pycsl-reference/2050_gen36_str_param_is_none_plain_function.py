r"""Test 2050 — gen #36 (expected PASS): `s is not None` on a `str` PARAMETER in a plain
function (no `@mutable_state`). At base the test fell through to route #44's INT sentinel,
`s = pycsl_none` — a Why3 type error (refused). Now it is route #51's OPAQUE string sentinel
(`str_eq_op s pycsl_none_str`), so the test is UNDECIDED: only claims true on BOTH branches
prove. Twins: 2051 / 2052 (must FAIL — neither branch may be decided).
"""
# pycsl-expected: PASS


#@ ensures \result >= 1
#@ assigns \nothing
def tag(s: str) -> int:
    if s is not None:
        return 1
    return 2
