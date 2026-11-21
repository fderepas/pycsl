"""Test 0059 — Python Reference 3.2.9.1: Import-related attributes on module objects

Route #251 (gen #36): expected PASS until route #251; expected FAIL now. The claim is TRUE (CPython
returns it), but the nested helper `add(a, b)` has UNANNOTATED parameters, i.e. `Any`, and `a + b` on them is
now the uninterpreted `pycsl_py_add` (a user dunder need not be integer arithmetic); the
caller's int instance is no longer decided. The price of the rule, as route #249's 1686 was.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 3
def test_user_defined_functions() -> int:
    """User-defined functions created by def statements."""
    def add(a, b):
        return a + b
    return add(1, 2)

if __name__ == "__main__":
    assert test_user_defined_functions() == 3
