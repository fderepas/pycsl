"""Test 0054 — CLI --fun: selective verification with dependency tracking"""
# pycsl-flags: --fun foobar
_ = 0  # anchor
#@ ensures \result == 2 * x
def double_int(x: int) -> int:
    """Doubles an integer."""
    return x + x

#@ ensures \result == 2 * x
def foobar(x: int) -> int:
    """Calls double_int."""
    return double_int(x)

# spec below intentionally wrong
#@ ensures \result == 4 * x
def some_other_fun(x: int) -> int:
    return x + x + 3

if __name__ == "__main__":
    assert double_int(3) == 6
    assert foobar(5) == 10
    print("PASS")
