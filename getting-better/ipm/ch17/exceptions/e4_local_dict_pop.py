from typing import Dict

#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
#@ no_exception KeyError
def f() -> int:
    d: Dict[int, int] = {}
    d.pop(1)
    return 0

if __name__ == "__main__":
    try:
        f(); print("returned")
    except KeyError:
        print("KeyError")
