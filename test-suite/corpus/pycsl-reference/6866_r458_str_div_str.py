r"""Test 6866 -- route #458 (expected FAIL): red team 36 witness `witnesses-r458/c29_r000_realistic_path.py` (MEASURED PROVED under `#@ no_exception \all` on main db6c57253): `base / name` with two `str` operands lowered as a path join; CPython TypeError. Refused PYCSL-R458-OPERAND-CLASSES.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

#@ no_exception \all
def f(base: str, name: str) -> int:
    full = base / name
    return len(full)


if __name__ == "__main__":
    try:
        r = f('/etc', 'hosts')
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
