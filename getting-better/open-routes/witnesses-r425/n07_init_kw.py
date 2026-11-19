#@ class invariant self.n >= 0
class A:
    #@ requires n >= 0
    def __init__(self, n: int) -> None:
        self.n = n

    #@ ensures \result >= 0
    #@ assigns \nothing
    def where(self) -> int:
        return self.n


#@ ensures \result >= 0
def g(a: A) -> int:
    a.__init__(n=-4)
    return a.where()


if __name__ == "__main__":
    try:
        r = g(A(1))
        if not (r >= 0):
            print("VIOLATION ensures", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
