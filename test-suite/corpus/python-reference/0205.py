"""Test 0205 — Python Reference 8.7: Function definitions

Route #251 (gen #36): expected PASS until route #251; expected FAIL now. The claim is TRUE (CPython
returns it), but the nested helper `double(x)` has UNANNOTATED parameters, i.e. `Any`, and `x * 2` on them is
now the uninterpreted `pycsl_py_mul` (a user dunder need not be integer arithmetic); the
caller's int instance is no longer decided. The price of the rule, as route #249's 1686 was.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 5
def test_function_definitions() -> int:
    """def creates a function."""
    def double(x):
        return x * 2
    return double(2) + 1

if __name__ == "__main__":
    assert test_function_definitions() == 5
