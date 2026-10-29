r"""Test 7035 -- route #456 (expected PASS): CONTROL -- `tags.difference(groups.values())` with `groups: Dict[str, str]`; PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Dict, Set
#@ no_exception \all
def f(tags: Set[str], groups: Dict[str, str]) -> int:
    rest = tags.difference(groups.values())
    return len(rest)
