from typing import Any, Dict, List


#@ requires True
#@ ensures \result == False
#@ assigns \nothing
def g(func: Dict[str, str]) -> bool:
    e: Dict[str, str] = func
    return "name" in e


def main() -> None:
    print(g({"name": "x"}))


if __name__ == "__main__":
    main()
