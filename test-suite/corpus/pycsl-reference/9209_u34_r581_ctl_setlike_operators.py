r"""Test 9209 -- route #581 CONTROL (expected PASS at base and HEAD): the operands route #581's rule judges on
every class pair are admitted when every pair is one CPython supports: an IfExp of two SETS (`set() if c else
{"q"}`) `|` a set, a dict's `.keys()` view `|` a set, and an empty `{}` beside a DICT arm (lvJ's typing) searched
with `in`. (`dict | dict` and `set | set` on parameters are not refused either, but fail Why3 typing at base and
HEAD -- unrelated to this route.)
"""
# pycsl-expected: PASS
from typing import Dict, Set

#@ no_exception \all
def sets(c: bool) -> int:
    x = set() if c else {"q"}
    return len(x | {"z"})

#@ no_exception \all
def keys_view(m: Dict[str, str]) -> int:
    return len(m.keys() | {"z"})

#@ no_exception \all
def empty_beside_dict(m: Dict[str, str], k: str, c: bool) -> int:
    y: Dict[str, str] = {} if c else m
    if k in y:
        return 1
    return 0

if __name__ == "__main__":
    print(sets(True), sets(False), keys_view({"a": "b"}), empty_beside_dict({"a": "b"}, "a", False))
