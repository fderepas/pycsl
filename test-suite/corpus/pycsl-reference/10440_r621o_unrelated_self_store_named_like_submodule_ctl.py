r"""Test 10440 -- run #9 u71, review rt79 r1, route #621 rule E control (PASS). The program imports only
zp40.k, and an unrelated class stores `self.b = 1`, where b is also the name of the submodule zp40/b.py.
`self` can never denote the package module object, so the store cannot rebind `zp40.b`; `cd <tree root> &&
python <this file>` prints "result 4". Base c115e0a5a PROVED it; u69 73f47db9d REFUSED it (rule E matched any
receiver); u71 narrows rule E to receivers rooted at an import-bound name (while no module object escapes).
"""
# pycsl-expected: PASS
from zp40.k import three


class C:
    def __init__(self) -> None:
        self.b = 1


#@ ensures \result == 4
def g() -> int:
    c = C()
    return c.b + three()


if __name__ == "__main__":
    print("result", g())
