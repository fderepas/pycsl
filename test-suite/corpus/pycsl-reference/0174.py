"""Test 0174 — PyCSL Annotation Reference 9.8 (variation A)"""
_ = 0  # anchor
import multi_file_lib.arith as m

#@ ensures \result == 3 * x
def call_triple_mod(x: int) -> int:
    return m.triple_int(x)

if __name__ == "__main__":
    print("PASS")
