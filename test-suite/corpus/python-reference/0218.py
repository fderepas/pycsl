"""Test 0218 — Python Reference 10.1: Full Grammar specification"""
_ = 0  # anchor
#@ ensures \result == 0
def test_full_grammar() -> int:
    """The full grammar specification defines Python syntax."""
    import ast
    tree = ast.parse("x = 1 + 2")
    assert isinstance(tree, ast.Module)
    return 0

if __name__ == "__main__":
    assert test_full_grammar() == 0
