# FALSE: f(False): C.g(1) raises ValueError, handler passes, else skipped -> `return y` UnboundLocalError.
# The try body reads no local, so the must-assign CFG has no exception edge into the handler.
class C:
    def __init__(self) -> None:
        self.n: int = 0

    @staticmethod
    #@ ensures \result == x
    #@ raises ValueError when x > 0
    #@ assigns \nothing
    def g(x: int) -> int:
        if x > 0:
            raise ValueError("p")
        return x

#@ ensures \result >= 0
#@ assigns \nothing
def f(c: bool) -> int:
    if c:
        y = 2
    try:
        C.g(1)
    except ValueError:
        pass
    else:
        y = 1
    return y

if __name__ == "__main__":
    print(f(False))
