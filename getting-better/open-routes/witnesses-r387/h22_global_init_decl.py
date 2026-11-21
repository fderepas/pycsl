#@ class invariant self.n >= 0
class C:
    global __init__

    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result >= 0
    #@ no_exception \all
    def get(self) -> int:
        return self.n


if __name__ == "__main__":
    try:
        r = C().get()
        print("no violation", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
