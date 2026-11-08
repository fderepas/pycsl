r"""Test 1938 — gen #36 (expected PASS): ROUTE #231 — CONTROL: a spec'd f-string whose value nothing claims about still verifies

The f-string that forgot its format spec: Module 5 dropped `FormattedValue.format_spec` and
`.conversion`, so `f"{v!c:spec}"` lowered exactly like `f"{v}"`. At 3ca32b8d the FAIL
witnesses of this family PROVED a contract CPython refutes.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == b + 1
#@ assigns \nothing
def f(b: int) -> int:
    msg = f"value {b:02x} / {b!r}"
    return b + 1
