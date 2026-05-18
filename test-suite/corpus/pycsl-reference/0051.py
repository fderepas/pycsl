"""Test 0051 — PyCSL Annotation Reference 2.1.6: Diverges"""
_ = 0  # anchor
#@ ensures \result >= 0
#@ \diverges
def infinite_loop(x: int) -> int:
    """Function marked as potentially non-terminating."""
    return infinite_loop(x)

if __name__ == "__main__":
    # Cannot run — would loop forever.
    print("PASS")
