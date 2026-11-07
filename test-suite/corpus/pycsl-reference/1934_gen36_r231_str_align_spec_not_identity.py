r"""Test 1934 — gen #36 (expected FAIL): ROUTE #231 — f"{s:>5}" == s is False for len(s) < 5 (left-padded)

The f-string that forgot its format spec: Module 5 dropped `FormattedValue.format_spec` and
`.conversion`, so `f"{v!c:spec}"` lowered exactly like `f"{v}"`. At 3ca32b8d the FAIL
witnesses of this family PROVED a contract CPython refutes.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 1
#@ assigns \nothing
def f(s: str) -> int:
    if f"{s:>5}" == s:
        return 1
    return 0
