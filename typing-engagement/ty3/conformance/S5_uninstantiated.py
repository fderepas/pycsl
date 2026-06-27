"""S5 STATIC gate — G5: an un-instantiated generic gets NO specialized copy.

Per the two-plane spec §1.4: a generic never instantiated emits NO specialized
WhyML; its declaration is checked for well-formedness only, and the soundness
report records it Ignored/GT8. No per-instance VC. This driver declares a
generic with no instantiation — it must NOT claim a per-instance theorem (D1).
"""
_ = 0
class Unused[T]:
    def __init__(self):
        self._v = 0
