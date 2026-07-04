"""WL-06 WRONG-REPR (low) — `bytes` param coarsens to `array int` (tau-blessed bytes=int†)
BUT `b[i]` routes to the opaque `val subscript_get (x:int)(i:int):int`, applied to
`b : array int` -> ill-typed (array int vs int). Not merely an opaque read (which would
be sound-but-uninformative): the emission is internally inconsistent and TYPEERRs.
Detector D2: TYPEERR. Borderline vs the tau-blessed bytes collapse — recorded because
the emission is BROKEN, not just coarse."""
_ = 0
def f(b: bytes, i: int) -> int:
    return b[i]
