"""Test 0342 — PyCSL Euclidean GCD (cross-validated Rocq + Lean axioms).

The classic Hoare-logic worked example, verified end-to-end under
full proof mode (no `--no-proof`, no `\\trusted`).

The GCD-related axioms (`gcd_0`, `gcd_step`, `gcd_divides_a`, etc.)
are imported via `#@ proof rocq` / `#@ proof lean` directives. Module6 emits each as a Why3 `axiom` block in the
preamble, sourcing the body from a hand-curated registry. The
registry's content is justified by the paired Rocq + Lean proofs in
`0342.proofs/{rocq,lean}/` — cross-validated manually for this MVP,
automatically once the `proof2why3` pipeline lands (see
docs/cross-validated-spec-sources.md).

The loop body uses the Euclidean identity `gcd(x, y) = gcd(y, x mod y)`
(axiom `gcd_step`) to preserve `gcd(x, y) == gcd(a, b)` across
iterations. At loop exit (`y = 0`), axiom `gcd_0` collapses the
invariant to `x == gcd(a, b)`, after which `gcd_divides_a` and
`gcd_divides_b` discharge the divisibility postconditions directly.
"""
#@ proof rocq Pycsl.Reference.Gcd.gcd_result_nonneg
#@ proof rocq Pycsl.Reference.Gcd.gcd_result_positive
#@ proof rocq Pycsl.Reference.Gcd.gcd_divides_a
#@ proof rocq Pycsl.Reference.Gcd.gcd_divides_b
#@ proof rocq Pycsl.Reference.Gcd.gcd_0
#@ proof rocq Pycsl.Reference.Gcd.gcd_step
#@ proof rocq Pycsl.Reference.Gcd.gcd_greatest
#@ proof lean Pycsl.Reference.Gcd.gcd_result_nonneg
#@ proof lean Pycsl.Reference.Gcd.gcd_result_positive
#@ proof lean Pycsl.Reference.Gcd.gcd_divides_a
#@ proof lean Pycsl.Reference.Gcd.gcd_divides_b
#@ proof lean Pycsl.Reference.Gcd.gcd_0
#@ proof lean Pycsl.Reference.Gcd.gcd_step
#@ proof lean Pycsl.Reference.Gcd.gcd_greatest
#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
#@ ensures (a > 0 or b > 0) ==> \result > 0
#@ ensures (a > 0 or b > 0) ==> a % \result == 0
#@ ensures (a > 0 or b > 0) ==> b % \result == 0
#@ ensures \result == gcd(a, b)
#@ ensures (a > 0 or b > 0) ==> (\forall k; (k > 0 and a % k == 0 and b % k == 0) ==> k <= \result)
#@ assigns \nothing
def gcd(a: int, b: int) -> int:
    x = a
    y = b
    #@ loop invariant x >= 0
    #@ loop invariant y >= 0
    #@ loop invariant gcd(x, y) == gcd(a, b)
    #@ loop invariant (a > 0 or b > 0) ==> (x > 0 or y > 0)
    #@ loop variant y
    while y != 0:
        r = x % y
        x = y
        y = r
    return x

if __name__ == "__main__":
    assert gcd(12, 18) == 6
    assert gcd(0, 7) == 7
    assert gcd(7, 0) == 7
    assert gcd(0, 0) == 0
    assert gcd(100, 75) == 25
    assert gcd(17, 13) == 1   # coprime
    print("PASS")
