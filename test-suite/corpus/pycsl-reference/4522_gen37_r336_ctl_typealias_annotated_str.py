r"""Test 4522 -- gen #37 route #336 (expected PASS): CONTROL: `x: S` (`S: TypeAlias = str`) and `y: Annotated[str, ..]`, `ensures \result == x` PROVES.
"""
# pycsl-expected: PASS
from typing import Annotated, TypeAlias
S: TypeAlias = str

#@ ensures \result == x
def same(x: S, y: Annotated[str, "tag"]) -> str:
    return x

if __name__ == "__main__":
    assert same("a", "b") == "a"
