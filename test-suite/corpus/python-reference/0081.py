"""Test 0081 — Python Reference 3.3.3.2: Resolving MRO entries"""
_ = 0  # anchor
#@ ensures \result == 0
def test_resolving_mro() -> int:
    """Method resolution order uses C3 linearization."""
    class A: pass
    class B(A): pass
    class C(A): pass
    class D(B, C): pass
    assert D.__mro__ == (D, B, C, A, object)
    return 0

if __name__ == "__main__":
    assert test_resolving_mro() == 0
