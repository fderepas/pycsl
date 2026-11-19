# FALSE (availability/total): `parse` recurses on itself forever; HAPPY total claims termination.
_ = 0  # anchor
#@ happy availability:
#@     targets parse
#@     total
class Parser:
    def __init__(self) -> None:
        self.k: int = 0

    #@ ensures \result >= 0
    #@ assigns \nothing
    def parse(self, n: int) -> int:
        return self.parse(n)

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100)
    print(Parser().parse(1))
