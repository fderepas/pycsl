"""S5 STATIC gate — G7/GT3: ParamSpec / TypeVarTuple are schema-only.

Per the two-plane spec §1.5: a generic using ParamSpec/TypeVarTuple is REJECTED
with a dedicated error code (schema-only, loud-fail). Must FAIL with
PYCSL-TY3-GT3.
"""
_ = 0
class C[**P]:
    def __init__(self):
        self._v = 0
