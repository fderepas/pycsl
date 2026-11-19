# lvU os.access: a CLASS named `os` (after `import os`) shadows the module; no tnames guard for os.
import os


class os:  # noqa
    #@ ensures \result == 7
    #@ assigns \nothing
    @staticmethod
    def access(p: str, m: int) -> int:
        d = {"a": 1}
        return d[p]


#@ no_exception KeyError
#@ assigns \nothing
def f() -> int:
    if os.access("x", 1):
        return 1
    return 0


if __name__ == "__main__":
    try:
        print("result", f())
    except KeyError as e:
        print("VIOLATION no_exception KeyError", e)
