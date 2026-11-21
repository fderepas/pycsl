#@ ensures \result == 6
def f() -> int:
    n = 2
    c = 0
    #@ loop invariant 0 <= i <= 6
    #@ loop invariant c == i
    #@ loop variant 6 - i
    #@ loop invariant c == 0 ==> n == 2
    #@ loop invariant c > 0 ==> n == 5
    for i in range(n + 1):
        n = 5
        c += 1
    return c

if __name__ == "__main__":
    assert f() == 6, f()
