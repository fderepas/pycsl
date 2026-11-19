r"""Test 5082 -- gen #37 route #376 (expected FAIL): NEW shape: a constructor local `r = R()` (route #309's `_current_record_var_classes` arm) with a collection default: `getattr(r, "k", {})` is the CLASS attribute `k = -1`, not `{}`; `v == {}` is False in CPython. REFUSED now (PYCSL-R376-GETATTR-CLASS-BINDING).
"""
# pycsl-expected: FAIL
class R:
    k = -1
    def __init__(self) -> None:
        self.x = 1

#@ ensures \result == 1
def f() -> int:
    r = R()
    v = getattr(r, "k", {})
    return 1 if v == {} else 0

if __name__ == "__main__":
    assert f() == 1, f()
