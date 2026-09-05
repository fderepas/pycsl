"""Test 0056 — Python Reference 3.2.8.7: Built-in methods"""
_ = 0  # anchor
#@ ensures \result == 1
#@ assigns \nothing
def test_built_in_methods() -> int:
    """Ref 3.2.8.7: a built-in method is a method of a built-in object — here `list`'s
    `append`, whose effect on the length the contract SAYS. Previously the whole body
    was `return 0` (relaunch #46, `bin/check-vacuous-drivers.py`)."""
    xs = [1, 2]
    xs.append(3)
    if len(xs) == 3 and xs[2] == 3:
        return 1
    return 0

if __name__ == "__main__":
    assert test_built_in_methods() == 1
