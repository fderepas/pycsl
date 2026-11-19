r"""Test 1937 — gen #36 (expected PASS): ROUTE #231 — CONTROL: a plain f-string still verifies a true property (f"{b}" == f"{b}")

The f-string that forgot its format spec: Module 5 dropped `FormattedValue.format_spec` and
`.conversion`, so `f"{v!c:spec}"` lowered exactly like `f"{v}"`. At 3ca32b8d the FAIL
witnesses of this family PROVED a contract CPython refutes.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == 1
#@ assigns \nothing
def f(b: int) -> int:
    if f"{b}" == f"{b}":
        return 1
    return 0
