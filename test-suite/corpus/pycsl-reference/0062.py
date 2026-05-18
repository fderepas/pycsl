"""Test 0062 — Multi-file: import mod (bare module import, dotted call)"""
_ = 0  # anchor
import multi_file_lib.arith

#@ ensures \result == 2 * x
def foobar(x: int) -> int:
    """Calls multi_file_lib.arith.double_int via full dotted name."""
    return multi_file_lib.arith.double_int(x)

if __name__ == "__main__":
    print("PASS")
