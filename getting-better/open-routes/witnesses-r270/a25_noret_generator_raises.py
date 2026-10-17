from typing import Iterator
# FALSE: fail() is a generator function: calling it only builds a generator (no ValueError),
# so f(False) reaches `return y` with y unbound -> UnboundLocalError (not ValueError).
#@ raises ValueError when True
#@ assigns \nothing
def fail() -> Iterator[int]:
    yield 1
    raise ValueError("x")

#@ ensures \result >= 0
#@ raises ValueError when not c
#@ assigns \nothing
def f(c: bool) -> int:
    if c:
        y = 1
    else:
        fail()
    return y

if __name__ == "__main__":
    try:
        print(f(False))
    except Exception as e:
        print(type(e).__name__, e)
