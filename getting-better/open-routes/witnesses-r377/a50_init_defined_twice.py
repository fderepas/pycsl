#@ class invariant self.n >= 5
class C:
    def __init__(self) -> None:
        self.n = 7

    def __init__(self) -> None:
        self.n = 0

    #@ ensures \result >= 5
    #@ assigns \nothing
    def get(self) -> int:
        return self.n

if __name__ == "__main__":
    print(C().get())
