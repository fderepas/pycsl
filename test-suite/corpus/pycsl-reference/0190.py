"""Test 0190 — PyCSL Annotation Reference 3.1.14: String equality in requires"""
_ = 0  # anchor
#@ requires a == "alpha"
#@ ensures \result == "alpha"
def echo_string(a: str) -> str:
    """Returns the same string that was required."""
    return a

if __name__ == "__main__":
    assert echo_string("alpha") == "alpha"
