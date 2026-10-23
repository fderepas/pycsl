r"""Test 1933 — gen #36 (expected FAIL): ROUTE #231 — f"{s!r}" == f"{s}" is False for every str (repr adds quotes)

The f-string that forgot its format spec: Module 5 dropped `FormattedValue.format_spec` and
`.conversion`, so `f"{v!c:spec}"` lowered exactly like `f"{v}"`. At 3ca32b8d the FAIL
witnesses of this family PROVED a contract CPython refutes.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 1
#@ assigns \nothing
def f(s: str) -> int:
    if f"{s!r}" == f"{s}":
        return 1
    return 0
