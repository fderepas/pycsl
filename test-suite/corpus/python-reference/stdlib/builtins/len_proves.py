"""len() on a list: returns non-negative integer.

Exercises the bare-builtin path (`len` resolves to `builtins.len`).
The stub contract for `len` ensures `\\result >= 0` for any input.
"""
# pycsl-flags: --no-proof
_ = 0  # anchor

#@ requires \length(arr) >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def list_length(arr: list) -> int:
    return len(arr)


if __name__ == "__main__":
    assert list_length([1, 2, 3]) == 3
