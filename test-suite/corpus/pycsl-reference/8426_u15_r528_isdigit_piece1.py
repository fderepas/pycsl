r"""Test 8426 -- route #528 (expected FAIL: PROVED at base, NOT PROVED: the PyCSL-R528 piece-index assertion; red team 49 probe k1024): `(s.split(",")[1]).isdigit()` on the lex-char-class computed-receiver arm; CPython IndexError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(s: str, i: int) -> int:
    return 1 if (s.split(",")[1]).isdigit() else 0


if __name__ == "__main__":
    try:
        r = f("a", 0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
