"""Test 0059 — Multi-file: import mod as alias (module-qualified calls)"""
_ = 0  # anchor
import multi_file_lib.arith as arith

#@ ensures \result == 2 * x
def foobar(x: int) -> int:
    """Calls arith.double_int via module alias."""
    return arith.double_int(x)

if __name__ == "__main__":
    print("PASS")
