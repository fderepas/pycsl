from typing import Dict, Any


#@ no_exception \all
#@ ensures \result == 1
def f(m: Dict[str, Any]) -> int:
    d = {m.get("a"): 1}
    return 1


if __name__ == "__main__":
    print(f({"a": [1]}))
