"""Test 0181 — PyCSL Annotation Reference 9.11 (variation B)"""
_ = 0  # anchor
import multi_file_lib.arith

#@ ensures \result == 5 * x
def bare_both(x: int) -> int:
    return multi_file_lib.arith.double_int(x) + multi_file_lib.arith.triple_int(x)

if __name__ == "__main__":
    print("PASS")
