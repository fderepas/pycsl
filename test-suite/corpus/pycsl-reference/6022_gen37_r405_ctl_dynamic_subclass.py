r"""Test 6022 -- gen #37 route #405 (expected PASS): CONTROL: `type(x)` with one argument, `type("T", (), {})` and `make_dataclass` without bases in the driver (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
import dataclasses


class B:
    def __init__(self) -> None:
        self.x: int = 1


#@ no_exception \all
#@ ensures \result == 1
def f(b: B) -> int:
    s = {b}
    return 1


if __name__ == "__main__":
    T = type("T", (), {})
    E = dataclasses.make_dataclass("E", [])
    print(f(B()), type(B()).__name__, T.__name__, E.__name__)
