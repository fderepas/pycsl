"""Test 0303 — Negative: \\proj index out of range for tuple2 — Why3 type error"""
# pycsl-expected: FAIL
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def bad_proj_arity(n: int) -> int:
    #@ ghost p : tuple2 = \mktuple(0, n)
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \proj(p, 2) >= 0
    #@ loop variant n - i
    while i < n:
        #@ ghost p = \mktuple(\fst(p) + 1, \snd(p) - 1)
        i = i + 1
    return i

if __name__ == "__main__":
    print("PASS")
