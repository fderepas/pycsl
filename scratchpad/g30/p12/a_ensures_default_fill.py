class C:
    def __init__(self):
        self.n: int = 0

    #@ requires True
    #@ ensures \result == k
    def f(self, k: int = 5) -> int:
        return k


#@ ensures \result == 99
def probe() -> int:
    k = 99
    c = C()
    return c.f()
