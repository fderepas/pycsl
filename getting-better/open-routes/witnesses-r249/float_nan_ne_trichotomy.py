#@ requires x != y
#@ ensures x < y or y < x
#@ assigns \nothing
def f(x: float, y: float) -> int:
    return 0


if __name__ == "__main__":
    x, y = float("nan"), 1.0
    print(x != y, x < y or y < x)  # True False
