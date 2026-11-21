r"""Test 4881 -- gen #37 route #360: CONTROL: `__slots__ = ("x", "__dict__")` admits any store; PROVES (CPython 1).
"""
class R:
    __slots__ = ("x", "__dict__")
    def __init__(self) -> None:
        self.x = 0
        self.y = 1

#@ no_exception \all
def f() -> int:
    r = R()
    return r.y

if __name__ == "__main__":
    print(f())
