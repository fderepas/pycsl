class C:
    def __init__(self) -> None:
        self.n: int = 0

    if False:
        #@ ensures \result == 1
        #@ assigns \nothing
        def get(self) -> int:
            return 1


#@ ensures \result == 1
def f(c: C) -> int:
    return c.get()


if __name__ == "__main__":
    try:
        r = f(C())
        print("VIOLATION f =", r) if r != 1 else print("no violation")
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
