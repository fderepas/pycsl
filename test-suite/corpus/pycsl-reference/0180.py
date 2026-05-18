"""Test 0180 — PyCSL Annotation Reference 9.11 (variation A)"""
_ = 0  # anchor
import multi_file_lib.arith

#@ ensures \result == 3 * x
def call_bare_triple(x: int) -> int:
    return multi_file_lib.arith.triple_int(x)

if __name__ == "__main__":
    print("PASS")
