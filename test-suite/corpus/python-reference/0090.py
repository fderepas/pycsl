"""Test 0090 — Python Reference 3.3.6: Emulating callable objects"""
_ = 0  # anchor
#@ ensures \result == 0
def test_emulating_callable() -> int:
    """__call__ makes instances callable."""
    class C:
        def __call__(self):
            return 42
    assert C()() == 42
    return 0

if __name__ == "__main__":
    assert test_emulating_callable() == 0
