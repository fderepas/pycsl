from typing import List
class W:
    def __sub__(self, o: object) -> int:
        return 1
    #@ ensures \result == 0
    def m(self) -> int:
        xs = [self]
        return xs[0] - xs[0]

if __name__ == "__main__":
    print(W().m())
