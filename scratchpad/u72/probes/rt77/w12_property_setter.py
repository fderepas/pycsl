class C:
    def __init__(self) -> None:
        self._v = 1

    @property
    def v(self) -> int:
        return self._v

    @v.setter
    def v(self, x: int) -> None:
        self._v = 2


#@ ensures \result == 1
def g() -> int:
    o = C()
    return o.v

if __name__ == "__main__":
    print(g())
