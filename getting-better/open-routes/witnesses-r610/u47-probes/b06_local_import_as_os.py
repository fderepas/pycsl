# u47: a function-local import BINDS `os` to another module (`import json as os`).
import os


#@ ensures \result == 1
def f(p: str) -> int:
    import json as os
    if os.access(p, 4):
        return 1
    return 1


if __name__ == "__main__":
    try:
        print("result", f("x"))
    except AttributeError as e:
        print("VIOLATION contract (raised)", e)
