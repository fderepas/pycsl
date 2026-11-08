class R:
    def __init__(self, nm: str) -> None:
        self.x = 0
        setattr(self, nm, [1])
#@ no_exception \all
def f(r: R) -> int:
    s = {r.x}
    return 0
if __name__ == "__main__":
    print(f(R("x")))
