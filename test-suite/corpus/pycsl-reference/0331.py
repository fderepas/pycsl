"""Test 0331 — minimal contract sanity (kept after the `#@ proof`
directive was removed on 2026-05-27; the file used to demo §2.1.11)."""
_ = 0  # anchor
#@ requires x >= 0
#@ ensures \result == x + 1
#@ assigns \nothing
def add_one(x: int) -> int:
    return x + 1

if __name__ == "__main__":
    assert add_one(0) == 1
    assert add_one(10) == 11
