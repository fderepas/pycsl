"""Test 0220 -- Rocq-required: four-accumulator product a*b*c*d.

SMT solvers (Alt-Ergo, Z3) timeout on this postcondition because proving it
requires multiplying 4 independent polynomial hypotheses together, producing
a degree-14 verification condition. Rocq nia tactic handles this.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires n >= 0
#@ ensures 1440 * \result == n * n * n * n * n * (n - 1) * (n - 1) * (n - 1) * (n - 1) * (n - 1) * (2 * n - 1) * (2 * n - 1) * (3 * n * n - 3 * n - 1)
def test_0220(n: int) -> int:
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
    return a * b * c * d

if __name__ == "__main__":
    for n_val in range(10):
        a = sum(k for k in range(n_val))
        b = sum(k ** 2 for k in range(n_val))
        c = sum(k ** 3 for k in range(n_val))
        d = sum(k ** 4 for k in range(n_val))
        result = a * b * c * d
        rhs = n_val ** 5 * (n_val - 1) ** 5 * (2 * n_val - 1) ** 2 * (3 * n_val ** 2 - 3 * n_val - 1)
        assert 1440 * result == rhs, f"n={n_val}: 1440*{result} != {rhs}"
    print("All assertions passed")
