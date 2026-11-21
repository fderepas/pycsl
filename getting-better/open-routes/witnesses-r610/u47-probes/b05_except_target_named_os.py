# u47: an EXCEPT target named `os` makes `os` a LOCAL of the function (deleted after the
# handler): `os.access` then raises UnboundLocalError in CPython, never the module query.
import os


#@ ensures \result == 1
def f(p: str) -> int:
    try:
        raise ValueError(p)
    except ValueError as os:
        pass
    if os.access(p, 4):
        return 1
    return 1


if __name__ == "__main__":
    try:
        print("result", f("x"))
    except UnboundLocalError as e:
        print("VIOLATION contract (raised)", e)
