_ = 0  # anchor
G: int = 0
#@ requires G == 0
#@ ensures \result == 0
def f() -> int:
    global G
    G = 7
    return G
if __name__ == "__main__":
    print(f())
