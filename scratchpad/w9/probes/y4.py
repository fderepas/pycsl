_ = 0  # anchor
class C:
    K: int = 7
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self) -> None:
        pass
    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    def g(self) -> int:
        return C.K
if __name__ == "__main__":
    print(C().g())
