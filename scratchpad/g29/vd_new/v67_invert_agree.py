"""v67 AGREE — `~x` is `-x - 1` on Python's unbounded ints: `~5` is -6."""


#@ ensures \result == 0 - 6
#@ assigns \nothing
def f() -> int:
    x: int = 5
    return ~x


if __name__ == "__main__":
    print(f())
