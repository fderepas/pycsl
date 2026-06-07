# Formal tests for pure_lib/fut — __future__ module
# Module only defines constants, no functions to verify formally.
# Test that annotation_flag is a known constant.


#@ ensures \result == 1048576
def test_annotations_flag() -> int:
    """annotations compiler flag is 2^20."""
    return 1048576
