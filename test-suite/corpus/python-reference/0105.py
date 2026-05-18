"""Test 0105 — Python Reference 4.2.3: Annotation scopes"""
_ = 0  # anchor
#@ ensures \result == 0
def test_annotation_scopes() -> int:
    """Ref 4.2.3: Annotation scopes."""
    return 0

if __name__ == "__main__":
    assert test_annotation_scopes() == 0
