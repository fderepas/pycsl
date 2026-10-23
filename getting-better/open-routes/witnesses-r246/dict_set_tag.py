from typing import Dict


#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[int, int]) -> int:
    if isinstance(d, set):
        return 1
    return 0


if __name__ == "__main__":
    print(f({}))
