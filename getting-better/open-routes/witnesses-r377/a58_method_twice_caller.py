class C:
    def __init__(self) -> None:
        self.n = 1

    #@ ensures \result == 1
    #@ assigns \nothing
    def get(self) -> int:
        return 1

    def get(self) -> int:
        return 2

#@ ensures \result == 1
def f(c: C) -> int:
    return c.get()

if __name__ == "__main__":
    print(f(C()))
