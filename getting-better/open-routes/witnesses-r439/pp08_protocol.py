from typing import Protocol
class Pr(Protocol):
    def __len__(self) -> int:
        ...


#@ no_exception \all
def f(c: Pr) -> int:
    s = {c}
    return len(s)


if __name__ == "__main__":
    try:
        r = f([1])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
