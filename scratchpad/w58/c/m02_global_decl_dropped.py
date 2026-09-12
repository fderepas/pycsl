G: int = 1

#@ ensures \result == 1
def f() -> int:
    global G
    G = 5
    return G

if __name__ == "__main__":
    print(f())
