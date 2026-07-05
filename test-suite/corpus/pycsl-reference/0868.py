"""Test 0868 — WL-06d regression lock (NEGATIVE twin of 0867). # pycsl-expected: FAIL

Guards the P3 ValueError-as-precondition on the bytes constructor. Python
`bytes([300])` raises `ValueError: bytes must be in range(0, 256)` — the function never
returns 300, it raises. BEFORE WL-06d the constructor `bytes_new` had NO range
precondition, so `bytes([300])[0] == 300` proved a FALSE normal-return (severity-1
unsound). WL-06d adds `requires forall i. 0<=x[i]<256`; the out-of-range element `300`
cannot discharge it, so this claim must NOT prove (fail-closed).

Prover note: pinned to Z3 (`# pycsl-flags: --prover Z3,,`) for a prompt refutation.
"""
# pycsl-expected: FAIL
# pycsl-flags: --prover Z3,,
_ = 0  # anchor


#@ ensures \result == 300
def ctor_oor_UNSOUND() -> int:
    """bytes([300]) raises ValueError in CPython — the range precondition on the
    constructor cannot be discharged, so this must NOT prove."""
    b = bytes([300])
    return b[0]


if __name__ == "__main__":
    try:
        _ = bytes([300])
        raise AssertionError("expected ValueError")
    except ValueError:
        pass
