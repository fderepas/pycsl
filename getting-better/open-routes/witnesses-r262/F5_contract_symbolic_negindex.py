# FALSE CLAIM: contract-side xs[k] with a SYMBOLIC negative k lowers to the raw Why3 map read
# xs[k] (an out-of-range cell no store touches) instead of Python's xs[len(xs)+k]; a literal
# xs[-1] IS normalised (n01 fails correctly). CPython: xs[-1] goes 0 -> 7.
from typing import List

#@ requires len(xs) == 2 and k == -1
#@ requires xs[1] == 0
#@ ensures xs[k] == \old(xs[k])
#@ assigns xs[1]
def f(xs: List[int], k: int) -> None:
    xs[1] = 7

if __name__ == "__main__":
    xs = [0, 0]; old = xs[-1]; f(xs, -1); print(xs[-1] == old, xs[-1], old)
