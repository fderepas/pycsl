from typing import List
class P:
    #@ no_exception \all
    def m(self) -> int:
        xs: List[int] = [self]
        return xs[0] + 1

if __name__ == "__main__":
    print(P().m())
