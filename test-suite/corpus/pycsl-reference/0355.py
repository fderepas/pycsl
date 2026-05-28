"""Test 0355 — no_exception parser: \\all wildcard form parses."""
_ = 0  # anchor
#@ requires True
#@ ensures \result == x + 1
#@ assigns \nothing
#@ no_exception \all
def increment(x: int) -> int:
    return x + 1


if __name__ == "__main__":
    assert increment(5) == 6
