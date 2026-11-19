_ = 0  # anchor
class C:
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self) -> None:
        pass
    @staticmethod
    #@ requires True
    #@ ensures \result == 99
    #@ assigns \nothing
    def s() -> int:
        return 1
    #@ requires True
    #@ ensures \result == 99
    #@ assigns \nothing
    def g(self) -> int:
        return C.s()
