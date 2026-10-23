_ = 0  # anchor


class Lib:
    def __init__(self) -> None:
        self.x: int = 0

    #@ ensures self.x == 5
    #@ no_inline
    def setx(self) -> int:
        self.x = 5
        return 0


_lib = Lib()


#@ ensures \result == 0
def caller() -> int:
    _lib.setx()
    return _lib.x
