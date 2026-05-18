"""Test 0129 — Python Reference 5.8.1: __main__.__spec__"""
_ = 0  # anchor
#@ ensures \result == 0
def test_module_spec() -> int:
    """ModuleSpec holds module metadata."""
    import importlib.util
    spec = importlib.util.find_spec("os")
    assert spec is not None
    return 0

if __name__ == "__main__":
    assert test_module_spec() == 0
