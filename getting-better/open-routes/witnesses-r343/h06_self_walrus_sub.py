class W:
    def __sub__(self, o: object) -> int:
        return 1
    #@ ensures \result == 0
    def m(self) -> int:
        return (s := self) - s

if __name__ == "__main__":
    print(W().m())
