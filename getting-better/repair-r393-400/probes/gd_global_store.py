class R:
    def __init__(self) -> None:
        self.x: int = 1
def setk(o: R) -> None:
    for o.k in [5]:
        pass
#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "k", 0)
if __name__ == "__main__":
    r = R(); setk(r); print("result", f(r))
