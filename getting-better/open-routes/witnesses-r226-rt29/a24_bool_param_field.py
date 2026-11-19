#@ class invariant self.n >= 1
class C:
    def __init__(self, b: bool) -> None:
        self.n = b

    #@ ensures \result >= 1
    #@ assigns \nothing
    def get(self) -> int:
        return self.n

if __name__ == "__main__":
    print(C(False).get())
