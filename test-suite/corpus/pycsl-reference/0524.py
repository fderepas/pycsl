"""Test 0524 — faithful KeyError dict read: a provably-present key proves.

The honest Python semantics: `dict[k]` on a missing key raises `KeyError` (it is
NOT an optimistic default read). PyCSL models this, opt-in, via
`#@ no_exception KeyError`: under it, a dict subscript read `d[k]` becomes a
proof obligation that the key is present (`Map.get d k <> None`,
`exception_model.py` trigger `("map_get", None)`). Here the key is set
immediately before the read, so the obligation discharges and the read is safe.

Negative companion: 0525 (an unproven key cannot discharge the obligation — that
IS the KeyError — and fails). no-more-int-3 A1 missing-key decision: faithful
KeyError.
"""
_ = 0  # anchor


#@ requires True
#@ ensures \result == 7
#@ assigns \nothing
#@ no_exception KeyError
def safe_read(k: int) -> int:
    d = {}
    d[k] = 7
    return d[k]
