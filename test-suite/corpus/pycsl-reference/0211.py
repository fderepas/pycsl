"""Test 0211 -- Rocq-required: sum products a*b^2*c.

SMT solvers (Alt-Ergo, Z3) timeout on this postcondition because proving it
requires multiplying 3 polynomial hypotheses together, producing a degree-12
verification condition. Rocq nia tactic handles this via algebraic certificates.
"""
# pycsl-expected: PASS
_ = 0  # anchor
#@ requires n >= 0
#@ ensures 288 * \result == n * n * n * n * n * (n - 1) * (n - 1) * (n - 1) * (n - 1) * (n - 1) * (2 * n - 1) * (2 * n - 1)
def test_0211(n: int) -> int:
    a = 0
    b = 0
    c = 0
    i = 0
    #@ loop invariant 2 * a == i * (i - 1)
    #@ loop invariant 6 * b == i * (i - 1) * (2 * i - 1)
    #@ loop invariant 4 * c == i * i * (i - 1) * (i - 1)
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        a = a + i
        b = b + i * i
        c = c + i * i * i
        i = i + 1
    return a * b * b * c

if __name__ == "__main__":
    for n_val in range(6):
        result = test_0211(n_val)
        rhs = n_val * n_val * n_val * n_val * n_val * (n_val - 1) * (n_val - 1) * (n_val - 1) * (n_val - 1) * (n_val - 1) * (2 * n_val - 1) * (2 * n_val - 1)
        assert 288 * result == rhs, f"n={n_val}: 288*{result} != {rhs}"
    print("All assertions passed")
