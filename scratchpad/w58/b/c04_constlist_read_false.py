from typing import List
CONST: List[int] = [1, 2, 3]

#@ ensures \result == 99
def f() -> int:
    return len(CONST)

if __name__ == "__main__":
    print(f())
