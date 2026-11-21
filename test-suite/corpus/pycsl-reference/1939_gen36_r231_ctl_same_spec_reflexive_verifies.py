r"""Test 1939 — gen #36 (expected PASS): ROUTE #231 — CONTROL: the SAME spec on the SAME operand is the same string (f"{b:02x}" == f"{b:02x}")

The f-string that forgot its format spec: Module 5 dropped `FormattedValue.format_spec` and
`.conversion`, so `f"{v!c:spec}"` lowered exactly like `f"{v}"`. At 3ca32b8d the FAIL
witnesses of this family PROVED a contract CPython refutes.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == 1
#@ assigns \nothing
def f(b: int) -> int:
    if f"{b:02x}" == f"{b:02x}":
        return 1
    return 0
