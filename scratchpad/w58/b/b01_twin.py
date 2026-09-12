from typing import Dict
CONST: Dict[str, int] = {"a": 1}

#@ ensures \result == 2
def f() -> int:
    CONST["a"] = 2
    return CONST["a"]

if __name__ == "__main__":
    print(f())
