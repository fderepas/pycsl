r"""Test 1910 — gen #32 (expected FAIL): ROUTE #227's ORDER arm.

FALSE OF THE PROGRAM: `None < None` raises `TypeError: '<' not supported between instances
of 'NoneType' and 'NoneType'`. At the parent commit the model DECIDED the comparison False
— because `pycsl_none < pycsl_none` is False for any integer — and so proved `\result == 0`
under `#@ no_exception \all`.

The arithmetic arm (1909) and this one are separate because a fix aimed at `+`/`-` alone
would have left the order relations, which is the same "one operator later" mistake route
#44's witness warned about. `==`/`!=` are deliberately NOT refused: `None == None` really is
`True`, and the opaque being SHARED rather than per-name is what makes that faithful
(control 1063).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 0
#@ no_exception \all
#@ assigns \nothing
def f() -> int:
    v = None
    if v < v:
        return 1
    return 0
