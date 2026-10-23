class G:
    v: int
    def __init__(self) -> None:
        self.v = 0

g = G()

#@ ensures \result == 5
def f() -> int:
    g.v = 5
    return g.v

if __name__ == "__main__":
    print(f())
