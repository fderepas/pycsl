"""Test 0352 — Euclidean GCD via parameter-mutation + tuple-unpack
(Rocq + Lean cross-validated).

Verifies the natural Python idiom:

    def gcd(a: int, b: int) -> int:
        while b != 0:
            a, b = b, a % b
        return a

Structurally distinct from 0342:
- Mutates the function parameters directly (no temp variable).
- Uses Python's tuple-unpacking idiom `a, b = b, a % b` (single
  statement — the canonical Euclidean step).

Contract postconditions reference the parameters `a`/`b` directly —
in Why3, parameters in the contract scope are immutable bindings to
the function's entry values, so `\\old(a)` and `a` denote the same
thing in `ensures` clauses. The loop invariant captures the
Euclidean identity `gcd(a, b) == gcd(\\old(a), \\old(b))` across
iterations, where the lhs `a, b` refer to the in-body refs and the
rhs picks up the parameter snapshot via `\\old`.

Exercises:
- Module6's parameter-mutation handling: formal parameters that are
  reassigned in the body get promoted to refs via `let a = ref a in`
  shadowing (see `_emit_body_code`).
- Module6's `_handle_tuple_unpack_stmt` on already-declared refs.
- The same seven cross-validated GCD axioms as 0342, imported via
  `#@ proof rocq` / `#@ proof lean` (load-bearing, namespace-aware).
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
    #@ ghost a0 = a
    #@ ghost b0 = b
    #@ loop invariant a >= 0
    #@ loop invariant b >= 0
    #@ loop invariant gcd(a, b) == gcd(a0, b0)
    #@ loop invariant (a0 > 0 or b0 > 0) ==> (a > 0 or b > 0)
    #@ loop variant b
    while b != 0:
        a, b = b, a % b
    return a

if __name__ == "__main__":
    assert gcd(12, 18) == 6
    assert gcd(0, 7) == 7
    assert gcd(7, 0) == 7
    assert gcd(0, 0) == 0
    assert gcd(100, 75) == 25
    assert gcd(17, 13) == 1   # coprime
    print("PASS")
