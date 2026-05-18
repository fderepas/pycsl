"""Test 0065 — Multi-file: circular import detection with --deep"""
_ = 0  # anchor
# pycsl-flags: --deep
from multi_file_lib.circ_a import func_a

#@ ensures \result == x + 2
def call_circ(x: int) -> int:
    """Calls func_a; circ_a↔circ_b have circular imports."""
    return func_a(x)

if __name__ == "__main__":
    print("PASS")
