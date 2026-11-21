from typing import Any, Dict
PyVal = Any

#@ requires True
#@ ensures \result == False
#@ assigns \nothing
def g(func: Dict[str, PyVal]) -> bool:
    e: Dict[str, PyVal] = func
    return "name" in e


def main() -> None:
    print(g({"name": 3}))


if __name__ == "__main__":
    main()
