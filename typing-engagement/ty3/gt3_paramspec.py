"""TY3 GT3 loud-fail — ParamSpec / TypeVarTuple are schema-only."""
_ = 0
class C[**P]:
    def __init__(self):
        self._v = 0
