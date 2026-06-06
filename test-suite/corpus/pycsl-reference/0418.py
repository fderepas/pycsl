"""Test 0418 -- 3-arg `range(start, stop, step)` desugar.

Exercises Phase1b_IrToStmt's range-with-step desugaring path
(case (b), 3-arg arm). The formal `ir_to_stmt` rewrites
`for i in range(start, stop, step): body` into
    SSeq (SAssign i start)
         (SWhile (CBoolLit true) (CInt 0)
                 (ECmp OpLt (EVar i) stop)
                 (SSeq body (SAugAssign i OpAdd step)))

The desugaring is structural only for positive `step` (negative
step would invert the loop condition direction).
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
#@ requires n >= 0
#@ ensures True
def sum_evens(n: int) -> int:
    """Sum of even integers in [0, n) using `range(0, n, 2)`."""
    total = 0
    for i in range(0, n, 2):
        total = total + i
    return total

if __name__ == "__main__":
    assert sum_evens(0) == 0
    assert sum_evens(1) == 0
    assert sum_evens(2) == 0
    assert sum_evens(5) == 0 + 2 + 4
    assert sum_evens(10) == 0 + 2 + 4 + 6 + 8
    print("All assertions passed")
