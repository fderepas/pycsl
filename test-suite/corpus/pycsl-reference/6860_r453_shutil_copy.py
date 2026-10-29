r"""Test 6860 -- route #453 (expected FAIL): red team 36 witness `witnesses-r453/c16_m020_realistic_backup.py` (MEASURED PROVED under `#@ no_exception \all` on main db6c57253): `shutil.copy(..)` admitted by its #161 method tail `copy`; CPython FileNotFoundError. Refused PYCSL-R453-MODULE-FUNCTION-NOT-ADMITTED.
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

import shutil



#@ no_exception \all
def f(path: str) -> int:
    shutil.copy(path, path + '.bak')
    return len(path)


if __name__ == "__main__":
    try:
        r = f('/nonexistent/rt36.cfg')
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
