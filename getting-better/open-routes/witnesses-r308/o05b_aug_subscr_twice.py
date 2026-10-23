from typing import List

#@ requires len(a) >= 1
#@ assigns a[0]
#@ ensures a[0] == \old(a[0]) + 1 and \result == \old(a[0])
def nxt(a: List[int]) -> int:
    r = a[0]
    a[0] = a[0] + 1
    return r

#@ ensures \result == 2
def f() -> int:
    cnt = [0]
    ys = [0, 0, 0]
    ys[nxt(cnt)] += 1
    return cnt[0]

if __name__ == "__main__":
    assert f() == 2
