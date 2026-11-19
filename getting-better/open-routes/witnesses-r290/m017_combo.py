from typing import List
import functools

#@ requires \length(xs) == 2
#@ ensures \result == 1
#@ assigns \nothing
def g1(xs: List[int]) -> int:
    getattr(xs, 'reverse')()
    return 1

#@ requires \length(xs) == 2
#@ ensures \result == 1
#@ assigns \nothing
def g2(xs: List[int]) -> int:
    xs.__delitem__(0)
    return 1

#@ requires \length(xs) == 2
#@ ensures \result == 1
#@ assigns \nothing
def g3(xs: List[int]) -> int:
    functools.partial(list.reverse, xs)()
    return 1

#@ requires \length(xs) == 2
#@ ensures \result == 1
#@ assigns \nothing
def g4(xs: List[int]) -> int:
    xs.__imul__(2)
    return 1

#@ ensures \result == 23
def f1() -> int:
    xs: List[int] = [3, 1]
    g1(xs)
    return len(xs) * 10 + xs[0]

#@ ensures \result == 23
def f2() -> int:
    xs: List[int] = [3, 1]
    g2(xs)
    return len(xs) * 10 + xs[0]

#@ ensures \result == 23
def f3() -> int:
    xs: List[int] = [3, 1]
    g3(xs)
    return len(xs) * 10 + xs[0]

#@ ensures \result == 23
def f4() -> int:
    xs: List[int] = [3, 1]
    g4(xs)
    return len(xs) * 10 + xs[0]

if __name__ == "__main__":
    print(f1(), f2(), f3(), f4())
    assert (f1(), f2(), f3(), f4()) == (23, 23, 23, 23)
