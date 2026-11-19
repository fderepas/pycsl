#@ ensures \result == 1
#@ assigns \nothing
def f(x: int) -> int:
    if isinstance(x, bool):
        return 1
    return 0


if __name__ == "__main__":
    print(f(5))
