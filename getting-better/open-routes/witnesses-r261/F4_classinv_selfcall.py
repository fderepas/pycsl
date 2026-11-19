# FALSE CLAIM: a() breaks the class invariant (n = -1) then calls self.peek(), whose contract
# (result >= 0) was proved ASSUMING the invariant; the sibling stub `self_peek_0 ()` takes no
# `self`, so neither the invariant nor peek's premise is checked at the call. CPython: -1.
#@ class invariant self.n >= 0
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result >= 0
    #@ assigns \nothing
    def peek(self) -> int:
        return self.n

    #@ ensures \result >= 0
    #@ assigns self.n
    def a(self) -> int:
        self.n = -1
        r = self.peek()
        self.n = 0
        return r

if __name__ == "__main__":
    print(C().a())
