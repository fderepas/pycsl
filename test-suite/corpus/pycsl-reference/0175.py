"""Test 0175 — PyCSL Annotation Reference 9.8 (variation B)"""
_ = 0  # anchor
import multi_file_lib.arith as lib

#@ ensures \result == 2 * x + 3 * x
def sum_via_mod(x: int) -> int:
    return lib.double_int(x) + lib.triple_int(x)

if __name__ == "__main__":
    print("PASS")
