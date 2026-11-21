class R:
    def __init__(self) -> None:
        self.x: int = 1
class S(R):
    try:
        raise ValueError()
    except ValueError as k:
        pass
    k = 5
#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)
if __name__ == "__main__":
    print("result", f(S()))
