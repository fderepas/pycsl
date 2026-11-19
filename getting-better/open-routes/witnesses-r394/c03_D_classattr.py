from dataclasses import dataclass


@dataclass
class D:
    x: int


class C:
    K = D(1)


#@ no_exception \all
def f() -> int:
    s = {C.K}
    return len(s)


if __name__ == "__main__":
    try:
        print("no violation", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
