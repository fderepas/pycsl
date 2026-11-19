# u47: a module-level `def sorted` shadows the builtin inside `",".join(sorted(xs))`; the user
# function MUTATES its argument (an effect the law-free builtin model drops).
from __future__ import annotations
from typing import List


#@ assigns xs
def sorted(xs: List[str]) -> List[str]:
    xs.append("q")
    return xs


#@ ensures len(xs) == \old(len(xs))
def j(xs: List[str]) -> str:
    return ",".join(sorted(xs))


if __name__ == "__main__":
    a = ["b", "a"]
    j(a)
    print("VIOLATION contract" if len(a) != 2 else "result", len(a))
