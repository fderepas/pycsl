from typing import Dict
CONST: Dict[str, int] = {"a": 1}

#@ assigns CONST
def poke() -> None:
    CONST["a"] = 2

#@ ensures \result == 1
def f() -> int:
    poke()
    return CONST["a"]

if __name__ == "__main__":
    print(f())
