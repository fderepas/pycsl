"""WL-06d SEVERITY-1 FIX (T10, P3) — out-of-range `bytes([...])` constructor now
FAIL-CLOSED. Verdict: UNPROVEN (was PROVEN — a severity-1 unsoundness).

Python `bytes([300])` raises `ValueError: bytes must be in range(0, 256)` — it never
returns 300. BEFORE WL-06d, `bytes_new` had NO range precondition, so
`bytes([300])[0]==300` proved a FALSE normal-return. WL-06d adds
`requires forall i. 0<=x[i]<256`; the element 300 cannot discharge it, so the claim now
fails closed. Pin to Z3 for a prompt refute."""
_ = 0


#@ ensures \result == 300
def ctor_oor_UNSOUND() -> int:
    b = bytes([300])
    return b[0]
