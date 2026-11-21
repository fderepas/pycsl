r"""Test 1959 — gen #36 (expected FAIL): NON-VACUITY twin of 1958 — the second pass uses a
DIFFERENT replacement (`\1-\2`), so `s == u` is not a consequence of determinism and the
claim must NOT prove (`re_sub_op` has no content law).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import re


#@ ensures \result == True
def two_pass_equals_nested(name: str) -> bool:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    s = re.sub(r"([A-Z])([A-Z][a-z])", r"\1-\2", s)
    u = re.sub(r"([A-Z])([A-Z][a-z])", r"\1_\2", re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name))
    return s == u
