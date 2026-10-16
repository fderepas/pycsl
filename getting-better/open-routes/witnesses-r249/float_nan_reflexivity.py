#@ ensures x == x
#@ assigns \nothing
def f(x: float) -> int:
    return 0


if __name__ == "__main__":
    x = float("nan")
    print(x == x)  # False
