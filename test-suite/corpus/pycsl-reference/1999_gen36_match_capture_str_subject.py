r"""Test 1999 — gen #36 (expected PASS): ROUTE #233 — a capture of a `str` subject is a `str` local

The bound local takes the subject's type: `r = t = s`.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == s
#@ assigns \nothing
def f(s: str) -> str:
    r = ""
    match s:
        case t:
            r = t
    return r
