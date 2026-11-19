r"""Test 8427 -- route #528 (expected FAIL: PROVED at base, NOT PROVED: the PyCSL-R528 piece-index assertion; red team 49 probe ak1003): `s.split(",")[1] in "ab"` on the lex-char-class enumerated-substring fold; CPython IndexError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(s: str, t: str) -> int:
    return 1 if s.split(",")[1] in "ab" else 0


if __name__ == "__main__":
    try:
        r = f("ab", ",")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
