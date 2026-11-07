from typing import List

#@ no_exception ZeroDivisionError
#@ ensures \result == 1
def g(n: int, xs: List[int]) -> int:
    t = (1, 10 // n)
    return 1

if __name__ == "__main__":
    try:
        print("VIOLATION contract", g(0, [0]))
    except ZeroDivisionError as e:
        print("VIOLATION ZeroDivisionError escapes a no_exception ZeroDivisionError claim", e)
