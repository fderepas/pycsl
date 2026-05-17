"""Test 0219 -- Rocq-required: squared four a^2*b*c*d.

SMT solvers (Alt-Ergo, Z3) timeout on this postcondition because proving it
requires multiplying 4 polynomial hypotheses together, producing a degree-16
verification condition. Rocq nia tactic handles this via algebraic certificates.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires n >= 0
#@ ensures 2880 * \result == n * n * n * n * n * n * (n - 1) * (n - 1) * (n - 1) * (n - 1) * (n - 1) * (n - 1) * (2 * n - 1) * (2 * n - 1) * (3 * n * n - 3 * n - 1)
def test_0219(n: int) -> int:
    a = 0
    b = 0
    c = 0
    d = 0
    i = 0
    #@ loop invariant 2 * a == i * (i - 1)
    #@ loop invariant 6 * b == i * (i - 1) * (2 * i - 1)
    #@ loop invariant 4 * c == i * i * (i - 1) * (i - 1)
    #@ loop invariant 30 * d == i * (i - 1) * (2 * i - 1) * (3 * i * i - 3 * i - 1)
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        a = a + i
        b = b + i * i
        c = c + i * i * i
        d = d + i * i * i * i
        i = i + 1
    return a * a * b * c * d

if __name__ == "__main__":
    for n_val in range(6):
        result = test_0219(n_val)
        rhs = n_val * n_val * n_val * n_val * n_val * n_val * (n_val - 1) * (n_val - 1) * (n_val - 1) * (n_val - 1) * (n_val - 1) * (n_val - 1) * (2 * n_val - 1) * (2 * n_val - 1) * (3 * n_val * n_val - 3 * n_val - 1)
        assert 2880 * result == rhs, f"n={n_val}: 2880*{result} != {rhs}"
    print("All assertions passed")
