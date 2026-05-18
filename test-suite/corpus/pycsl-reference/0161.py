"""Test 0161 — PyCSL Annotation Reference 2.1.7 (variation B): trusted caller"""
_ = 0  # anchor
#@ ensures \result == x + 10
#@ \trusted
def add_ten(x: int) -> int:
    """Trusted function."""
    return x + 10

#@ ensures \result == x + 11
def add_eleven(x: int) -> int:
    """Calls trusted add_ten."""
    return add_ten(x) + 1

if __name__ == "__main__":
    assert add_eleven(5) == 16
