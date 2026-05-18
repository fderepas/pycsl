"""Test 0163 — PyCSL Annotation Reference 2.1.7 (variation B): trusted multiple callers"""
_ = 0  # anchor
#@ ensures \result == x + 1
#@ \trusted
def inc(x: int) -> int:
    """Trusted increment."""
    return x + 1

#@ ensures \result == x + 2
def add_two(x: int) -> int:
    """Two calls to trusted inc."""
    return inc(inc(x))

if __name__ == "__main__":
    assert add_two(3) == 5
