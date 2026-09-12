class K:
    v: int
    def __init__(self) -> None:
        self.v = 1
    #@ ensures \result == 1
    def f(self) -> int:
        del self.v
        return self.v
if __name__ == "__main__":
    print(K().f())
