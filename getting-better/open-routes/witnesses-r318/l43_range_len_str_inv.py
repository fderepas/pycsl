#@ ensures \result == 1
def f() -> int:
    s = "abcd"
    c = 0
    #@ loop invariant 0 <= i <= 1
    #@ loop invariant c == i
    #@ loop variant 6 - i
    #@ loop invariant c == 0 ==> s == "abcd"
    #@ loop invariant c > 0 ==> s == "a"
    for i in range(len(s)):
        c += 1
        s = "a"
    return c

if __name__ == "__main__":
    assert f() == 1, f()
