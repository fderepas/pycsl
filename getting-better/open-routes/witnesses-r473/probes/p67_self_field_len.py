from typing import List


#@ requires len(c) >= 1
#@ ensures True
#@ assigns \nothing
def g(c: List[int]) -> int:
    return c[0]


#@ requires len(c) >= 2
#@ ensures True
#@ assigns \nothing
def g2(c: List[int]) -> int:
    return c[1]


#@ requires True
#@ ensures \result == len(c)
#@ assigns \nothing
def ln(c: List[int]) -> int:
    return len(c)


class K:
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self) -> None:
        self.xs: List[int] = [5]

    #@ requires len(self.xs) >= 1
    #@ ensures True
    #@ assigns \nothing
    def get(self) -> int:
        return self.xs[0]


class K3:
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self) -> None:
        self.xs: List[int] = [5]

    #@ requires True
    #@ ensures \result == 1024
    #@ assigns self.xs
    def h(self) -> int:
        self.xs = []
        return len(self.xs)


if __name__ == "__main__":
    try:
        print("result", K3().h())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
