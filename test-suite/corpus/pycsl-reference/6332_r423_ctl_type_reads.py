r"""Test 6332 -- route #423 (expected PASS): CONTROL: `type` / a file metaclass read as a value only where no class is created -- `isinstance(x, type)`, `type(x).__name__`, `type(x) is int`, a metaclass= keyword, `type("D", (), {})` with the literal bases `()` -- then `{b}` under `no_exception \all` (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
class M(type):
    pass


class B(metaclass=M):
    def __init__(self) -> None:
        self.x: int = 1


#@ no_exception \all
def f(b: B) -> int:
    s = {b}
    return len(s)


def g(x: int) -> bool:
    return isinstance(x, type) or type(x) is int or type(x).__name__ == "int"


if __name__ == "__main__":
    D = type("D", (), {})
    print(f(B()), g(1), D.__name__)
