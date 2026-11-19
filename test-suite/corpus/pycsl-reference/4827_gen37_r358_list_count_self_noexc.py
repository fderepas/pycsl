r"""Test 4827 -- gen #37 route #358 (expected FAIL): shape: `xs.count(self)` with a raising user `__eq__` under `no_exception \all` (FAILED at base by the `__eq__` raise analysis); FAIL (PyCSL-R358: a list method handed an erased argument).
"""
# pycsl-expected: FAIL
from typing import List

class P:
    def __eq__(self, o: object) -> bool:
        raise ValueError("eq")
    __hash__ = object.__hash__

    #@ no_exception \all
    def m(self, xs: List[int]) -> int:
        if len(xs) == 0:
            return 0
        return xs.count(self)


if __name__ == "__main__":
    try:
        P().m([1])
        assert False, "expected ValueError"
    except ValueError:
        pass
