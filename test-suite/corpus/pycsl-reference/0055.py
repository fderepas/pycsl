"""Test 0055 — CLI --fun: verify single function without dependencies"""
# pycsl-flags: --fun double_int
_ = 0  # anchor
#@ ensures \result == 2 * x
def double_int(x: int) -> int:
    """Doubles an integer."""
    return x + x

# spec below intentionally wrong
#@ ensures \result == 4 * x
def some_other_fun(x: int) -> int:
    return x + x + 3

if __name__ == "__main__":
    assert double_int(3) == 6
    print("PASS")
