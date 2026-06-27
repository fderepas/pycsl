"""TY3 bound check — `C[T: int]` instantiated with `str` is rejected (GT2).

The bound is an instantiation-time obligation (invariant checking per GT2).
`C[T: int]` instantiated with `int` is admissible; with `str` is rejected.
"""
_ = 0
class C[T: int]:
    def __init__(self):
        self._v = 0

if __name__ == "__main__":
    c = C[str]()
