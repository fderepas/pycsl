r"""Test 10496 -- run #9 u75, review rt83 o5 (u73 INTRODUCED over-refusal, PASS). A parameter annotation
`List[int]` (`from typing import List`) beside an unrelated `self.b = 1` (b is also a submodule name of the
package zu75g the walk meets): a typing alias is no module object, so the annotation is no module escape and
the store stays unjudged; `cd <tree root> && python <this file>` prints "result 4" and pycsl proves it
(u73 refused it with PYCSL-SEM-IMPORT-PACKAGE-SUBMODULE-REBOUND).
"""
# pycsl-expected: PASS
from typing import List
from zu75g.k import three


class C:
    def __init__(self) -> None:
        self.b = 1


#@ ensures \result == 4
def g(xs: List[int]) -> int:
    c = C()
    return c.b + three()


if __name__ == "__main__":
    print("result", g([1]))
