from typing import List
CONST: List[int] = [1, 2, 3]

#@ ensures \result == 1
def f() -> int:
    CONST[0] = 9
    return CONST[0]

if __name__ == "__main__":
    print(f())
