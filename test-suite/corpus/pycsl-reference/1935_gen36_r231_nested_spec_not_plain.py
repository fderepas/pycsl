r"""Test 1935 — gen #36 (expected FAIL): ROUTE #231 — a nested spec f"{b:{w}}" is not f"{b}" (w == 5 pads: "   10" vs "10")

The f-string that forgot its format spec: Module 5 dropped `FormattedValue.format_spec` and
`.conversion`, so `f"{v!c:spec}"` lowered exactly like `f"{v}"`. At 3ca32b8d the FAIL
witnesses of this family PROVED a contract CPython refutes.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires b == 10
#@ requires w == 5
#@ ensures \result == 1
#@ assigns \nothing
def f(b: int, w: int) -> int:
    if f"{b:{w}}" == f"{b}":
        return 1
    return 0
