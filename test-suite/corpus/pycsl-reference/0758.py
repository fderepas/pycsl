"""Test 0758 — cleared-hash.md S7: NEGATIVE driver (genuinely-false key claim stays unprovable).

A control on the faithful model: distinct keys hold INDEPENDENT values, so `d["a"] == d["b"]` is
genuinely FALSE after writing them different values. The verifier must NOT prove it (a `map string`
model that proved this would be unsound / vacuous). Expected UNPROVEN — the non-aliasing that makes
0755/0756/0757 provable is exactly what makes this false claim unprovable."""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
#@ no_exception KeyError
def distinct_values_differ() -> int:
    d = {}
    d["a"] = 1
    d["b"] = 2
    # FALSE: d["a"] (=1) != d["b"] (=2); the claim \result == 0 via this equality cannot hold.
    if d["a"] == d["b"]:
        return 0
    return 1
