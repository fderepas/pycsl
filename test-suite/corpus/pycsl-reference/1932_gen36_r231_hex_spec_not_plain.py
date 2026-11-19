r"""Test 1932 — gen #36 (expected FAIL): ROUTE #231 — f"{b:02x}" == f"{b}" is False for b == 10 ("0a" vs "10")

The f-string that forgot its format spec: Module 5 dropped `FormattedValue.format_spec` and
`.conversion`, so `f"{v!c:spec}"` lowered exactly like `f"{v}"`. At 3ca32b8d the FAIL
witnesses of this family PROVED a contract CPython refutes.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires b == 10
#@ ensures \result == 1
#@ assigns \nothing
def f(b: int) -> int:
    if f"{b:02x}" == f"{b}":
        return 1
    return 0
