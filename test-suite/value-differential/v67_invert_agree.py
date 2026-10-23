"""v67 AGREE — `~x` is `-x - 1` on Python's unbounded ints, so `~5 + 10` is 4 (not the 5 that plain negation would give). Written without a negative literal because the plane's claim parser reads a single integer."""


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    x: int = 5
    return ~x + 10


if __name__ == "__main__":
    print(f())
