r"""Test 1706 - ROUTE #203 completeness control (gen #30): the repair is a VALUE-KEYED opaque, not `any`, and this witness is what pins the difference. `str_of_int_hash` is deterministic, so two f-strings interpolating the SAME value are the same string - which is what Python says - and that stays provable. A "simplification" to `(any int)`, fresh at every evaluation, would still pass 1705 and would silently lose this.
"""
# pycsl-expected: PASS

_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    n = 5
    a = f"{n}"
    b = f"{n}"
    if a == b:
        return 1
    return 2
