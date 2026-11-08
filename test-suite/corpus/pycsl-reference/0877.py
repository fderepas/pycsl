"""Test 0877 — tier3-p1 tag-normalization soundness lock (NEGATIVE twin of 0876). # pycsl-expected: FAIL

The soundness floor for the upstream-tag normalization exercised by 0876. With
`xs = [a, b]` the faithful lowering gives `xs[0] + xs[1] == a + b`, never `a + b + 1`.
The contract CLAIMS `\result == a + b + 1`, which is FALSE of the faithful lowering
(off by one), so it must remain UNPROVEN. If this test ever PASSES,
the `List`->`ArrayLit` / `Compare`/`BoolOp`->`BinOp` normalization has become unsound
(a wrong-value lowering proved green — severity-1).
"""
# pycsl-expected: FAIL


#@ requires a >= 0 and a <= 100
#@ requires b >= 0 and b <= 100
#@ ensures \result == a + b + 1
def norm_unsound(a: int, b: int) -> int:
    xs = [a, b]              # List -> ArrayLit; `a >= 0 and ...` -> Compare/BoolOp -> BinOp
    return xs[0] + xs[1]
