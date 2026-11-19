from typing import List
CONST: List[int] = [1, 2, 3]

#@ ensures \result == 3
def f() -> int:
    CONST.append(4)
    return len(CONST)

if __name__ == "__main__":
    print(f())
