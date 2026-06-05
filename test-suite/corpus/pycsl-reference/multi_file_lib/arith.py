"""multi_file_lib.arith — basic contracted arithmetic helpers (cross-module test fixture)."""
_ = 0  # anchor


#@ ensures \result == 2 * x
def double_int(x: int) -> int:
    return x + x


#@ ensures \result == 3 * x
def triple_int(x: int) -> int:
    return x + x + x
