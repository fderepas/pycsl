"""Test 0334 — PyCSL Tuple return (cross-prover, tuesday-01 fixture).

Exercises `\\result[0]` / `\\result[1]` indexing on a tuple-returning
function. The `requires b != 0` clause is needed by Alt-Ergo to
discharge the division-by-zero safety obligation; the cross-prover
contract pair (rocq/lean) carries this as a body implication in the
ensures clauses, which is the form the bridge produces.
"""
#@ requires b != 0
#@ ensures (b != 0) ==> (\result[0] == (a // b))
#@ ensures (b != 0) ==> (\result[1] == (a % b))
#@ assigns \nothing
def divmod_pair(a: int, b: int) -> tuple:
    return (a // b, a % b)

if __name__ == "__main__":
    assert divmod_pair(7, 2) == (3, 1)
    assert divmod_pair(10, 3) == (3, 1)
    assert divmod_pair(0, 5) == (0, 0)
