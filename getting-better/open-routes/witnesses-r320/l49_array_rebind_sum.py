from typing import List
#@ ensures \result != 10
def f() -> int:
    xs = [1, 2, 3, 4]
    t = 0
    c = 0
    #@ loop invariant c >= 0
    #@ loop invariant c == 0 ==> t == 0 and xs[0] == 1 and xs[1] == 2 and xs[2] == 3 and xs[3] == 4
    #@ loop invariant c > 0 ==> xs[0] == 100 and xs[1] == 100 and xs[2] == 100 and xs[3] == 100
    #@ loop invariant c == 1 ==> 1 <= t and t <= 4
    #@ loop invariant c >= 2 ==> t >= 101
    for x in xs:
        t += x
        xs = [100, 100, 100, 100]
        c += 1
    return t

if __name__ == "__main__":
    assert f() != 10, f()
