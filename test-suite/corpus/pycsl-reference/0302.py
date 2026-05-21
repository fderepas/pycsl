"""Test 0302 — Negative: \\proj with dynamic (non-literal) index — Module4 error"""
# pycsl-expected: FAIL
_ = 0  # anchor

#@ requires n >= 0 and n < 2
#@ ensures \proj(p, n) >= 0
#@ assigns \nothing
def bad_dynamic_proj(n: int) -> int:
    #@ ghost p : tuple2 = \mktuple(10, 20)
    return 0

if __name__ == "__main__":
    print("PASS")
