class A:
    k = -1

class W(A):
    #@ ensures \result >= 0
    def m(self) -> int:
        return getattr(self, "k", 0)

if __name__ == "__main__":
    assert W().m() >= 0, W().m()
