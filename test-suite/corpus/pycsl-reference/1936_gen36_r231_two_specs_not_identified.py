r"""Test 1936 — gen #36 (expected FAIL): ROUTE #231 — two different specs are not identified: f"{b:x}" == f"{b:X}" is False for b == 10 ("a" vs "A")

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
    if f"{b:x}" == f"{b:X}":
        return 1
    return 0
