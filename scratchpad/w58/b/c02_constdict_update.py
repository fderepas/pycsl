from typing import Dict
CONST: Dict[str, int] = {"a": 1}

#@ ensures \result == 1
def f() -> int:
    CONST["b"] = 2
    return len(CONST)

if __name__ == "__main__":
    print(f())
