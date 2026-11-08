r"""Test 1958 — gen #36 (expected PASS): a RE-ASSIGNED local whose first binding is a
`re.sub(...)` call is a STRING local. `re.sub` lowers to the deterministic
`val function re_sub_op (pat rep s: string) : string` and `_is_string_expr` already
classified it as a string, but the pre-declaration classifier
(`_collect_str_call_result_locals`) did not, so a local assigned twice was pre-declared
`ref 0` and its `:=` failed the Why3 type check (L3-tc). Now `s` is `ref (re_sub_op ..)`,
the second `re.sub(.., s)` reads it as a string, and the composed value equals the
nested call (determinism). Twin: 1959 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
import re


#@ ensures \result == True
def two_pass_equals_nested(name: str) -> bool:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    s = re.sub(r"([A-Z])([A-Z][a-z])", r"\1_\2", s)
    u = re.sub(r"([A-Z])([A-Z][a-z])", r"\1_\2", re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name))
    return s == u
