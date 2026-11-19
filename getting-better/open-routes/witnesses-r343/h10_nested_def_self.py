class W:
    def __sub__(self, o: object) -> int:
        return 1
    #@ ensures \result == 0
    def m(self) -> int:
        t = self
        u = t
        return u - t

if __name__ == "__main__":
    print(W().m())
