#@ class invariant self.y >= 0
class C:
    def __init__(self, x: int) -> None:
        self.x = x
        self.y = self.x

    #@ ensures \result >= 0
    #@ assigns \nothing
    def get(self) -> int:
        return self.y

if __name__ == "__main__":
    print(C(-1).get())
